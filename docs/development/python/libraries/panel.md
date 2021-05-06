# Panel

Developer notes from usage of the [Panel](https://panel.holoviz.org/index.html) library.

# Notes

Any control without a callback function feature like "on\_click" for the button can gain
a callback function using the param.watch method.  For example, a Checkbox.  Suppose, you
would like to have an event when the checkbox is toggled.  

Here is the code to create the checkbox control:
```
logEnableControl = pn.widgets.Checkbox(name="Enable file logging")
```

To setup a watch for a change in the "value" property, use:
```
logEnableControl.param.watch(logEnableCallback, 'value')
```

The callback function should trap the emitted event:
```
def logEnableCallback(event):
    print(event)
```

Which will result in something like:
```text
Event(what='value', name='value', obj=Checkbox(name='Enable file logging', value=True), cls=Checkbox(name='Enable file logging', value=True), old=False, new=True, type='changed')
```
