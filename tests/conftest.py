import sys
import mock


class FakeCollectdModule(object):
    info = mock.Mock()
    warning = mock.Mock()
    register_config = mock.Mock()
    register_read = mock.Mock()
    Values = mock.Mock()


class DBusException(Exception):
    pass


class FakeDbusModule(object):
    SystemBus = mock.Mock()
    Interface = mock.Mock()
    exceptions = mock.Mock(DBusException=DBusException)


sys.modules['collectd'] = FakeCollectdModule()
sys.modules['dbus'] = FakeDbusModule()
