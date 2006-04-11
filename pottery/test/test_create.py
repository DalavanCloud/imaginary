

from zope.interface import Interface, implements, directlyProvides

from twisted.trial import unittest

from axiom import item, attributes

from pottery.test import commandutils
from pottery import ipottery, plugins, action, objects


class IFoo(Interface):
    pass



class Foo(item.Item):
    implements(IFoo)

    foo = attributes.text()

    def installOn(self, other):
        other.powerUp(self, IFoo)


def createFoo(store, name, description):
    o = objects.Object(store=store, name=name, description=description)
    Foo(store=store).installOn(o)
    return o


class FooPlugin(object):
    directlyProvides(ipottery.IObjectType)

    type = 'foo'

    def getType(cls):
        return createFoo
    getType = classmethod(getType)



class CreateTest(commandutils.CommandTestCaseMixin, unittest.TestCase):
    def _getPlugins(self, iface, package):
        self.assertIdentical(iface, ipottery.IObjectType)
        self.assertIdentical(package, plugins)
        return [FooPlugin]


    def setUp(self):
        self.old_getPlugins = action.getPlugins
        action.getPlugins = self._getPlugins
        return commandutils.CommandTestCaseMixin.setUp(self)


    def tearDown(self):
        action.getPlugins = self.old_getPlugins
        return commandutils.CommandTestCaseMixin.tearDown(self)


    def testCreate(self):
        self._test(
            "create foo bar",
            ["bar created."],
            ["Test Player creates bar."])
        foobar = self.player.find("bar")
        self.assertEquals(foobar.name, "bar")
        self.assertEquals(foobar.description, "an undescribed object")
        self.assertEquals(foobar.location, self.player)
        self.failUnless(isinstance(IFoo(foobar), Foo))

        self._test(
            "create foo 'bar foo'",
            ["bar foo created."],
            ["Test Player creates bar foo."])
        barfoo = self.player.find("bar foo")
        self.assertEquals(barfoo.name, "bar foo")
        self.assertEquals(barfoo.description, 'an undescribed object')
        self.assertEquals(barfoo.location, self.player)

        self._test(
            "create foo 'described thing' This is the things description.",
            ["described thing created."],
            ["Test Player creates described thing."])
        thing = self.player.find("described thing")
        self.assertEquals(thing.name, "described thing")
        self.assertEquals(thing.description, "This is the things description.")
        self.assertEquals(thing.location, self.player)
