from behave import *


@given(u'the program is running')
def step_impl(context):
    assert True


@when(u'task A is requested')
def step_impl(context):
    assert True


@then(u'task A should be done')
def step_impl(context):
    assert True
