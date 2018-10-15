import mock
import pytest
import dbus
import collectd_systemd


@pytest.fixture
def conf_bare():
    return mock.Mock(children=[
        mock.Mock(key='Interval', values=[120.0]),
    ])


@pytest.fixture
def conf_valid(conf_bare):
    conf_bare.children.extend([
        mock.Mock(key='Verbose', values=['tRuE']),
        mock.Mock(key='Service', values=['service1','service2']),
        mock.Mock(key='Service', values=['service3']),
    ])
    return conf_bare


@pytest.fixture
def conf_invalid(conf_bare):
    conf_bare.children.append(mock.Mock(key='Foo', values=[1]))
    return conf_bare


@pytest.fixture
def mon():
    return collectd_systemd.SystemD()


@pytest.fixture
def configured_mon(mon, conf_valid):
    mon.configure_callback(conf_valid)
    return mon


def test_configure(mon, conf_valid):
    with mock.patch('collectd.register_read') as m:
        mon.configure_callback(conf_valid)
        m.assert_called_once_with(mon.read_callback, mock.ANY)
    assert hasattr(mon, 'bus')
    assert hasattr(mon, 'manager')
    assert mon.interval == 120.0
    assert mon.verbose_logging
    assert len(mon.services) == 3


def test_configure_does_nothing_if_no_services(mon, conf_bare):
    with mock.patch.object(mon, 'init_dbus') as m:
        mon.configure_callback(conf_bare)
        m.assert_not_called()
    assert not mon.verbose_logging


def test_configure_invalid_setting(mon, conf_invalid):
    with pytest.raises(ValueError):
        mon.configure_callback(conf_invalid)


def test_get_unit(configured_mon):
    u = configured_mon.get_unit('foo')
    assert u is not None
    with mock.patch('dbus.Interface', side_effect=dbus.exceptions.DBusException):
        u = configured_mon.get_unit('missing')
        assert u is None


def test_get_service_state(configured_mon):
    with mock.patch.object(configured_mon, 'get_unit') as m:
        m().Get.return_value = 'running'
        state = configured_mon.get_service_state('foo')
        assert state == 'running'
    with mock.patch('dbus.Interface', side_effect=dbus.exceptions.DBusException):
        state = configured_mon.get_service_state('missing')
        assert state == 'broken'
    with mock.patch.object(configured_mon, 'get_unit') as m:
        m().Get.side_effect=dbus.exceptions.DBusException
        state = configured_mon.get_service_state('broken-cache')
        assert state == 'broken'


def test_send_metrics(configured_mon):
    with mock.patch.object(configured_mon, 'get_service_state') as m:
        m.side_effect = ['running', 'failed', 'running']
        with mock.patch('collectd.Values') as val_mock:
            configured_mon.read_callback()
            assert val_mock.call_count == 3
            c1_kwargs = val_mock.call_args_list[0][1]
            assert c1_kwargs['plugin_instance'] == 'service1'
            assert c1_kwargs['values'] == [1]
            c2_kwargs = val_mock.call_args_list[1][1]
            assert c2_kwargs['plugin_instance'] == 'service2'
            assert c2_kwargs['values'] == [0]
            c3_kwargs = val_mock.call_args_list[2][1]
            assert c3_kwargs['plugin_instance'] == 'service3'
            assert c3_kwargs['values'] == [1]


def test_retry_if_broken(configured_mon):
    with mock.patch.object(configured_mon, 'get_service_state') as m:
        m.side_effect = ['broken', 'running', 'failed', 'running']
        with mock.patch.object(configured_mon, 'init_dbus') as idm:
            with mock.patch('collectd.Values') as val_mock:
                configured_mon.read_callback()
                idm.assert_called_once()
                assert m.call_count == 4
                m.call_args_list[0][0][0] == m.call_args_list[1][0][0] == 'service1'
                assert val_mock.call_count == 3
                c1_kwargs = val_mock.call_args_list[0][1]
                assert c1_kwargs['plugin_instance'] == 'service1'
                assert c1_kwargs['values'] == [1]
                c2_kwargs = val_mock.call_args_list[1][1]
                assert c2_kwargs['plugin_instance'] == 'service2'
                assert c2_kwargs['values'] == [0]
                c3_kwargs = val_mock.call_args_list[2][1]
                assert c3_kwargs['plugin_instance'] == 'service3'
                assert c3_kwargs['values'] == [1]