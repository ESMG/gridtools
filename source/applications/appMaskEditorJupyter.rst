.. _jupyter-mask-editor-application:

*******************
Jupyter Mask Editor
*******************

Once a model grid is read and a map projection created, the application
can be launched with these commands in a jupyter notebook cell::

    # Set a map projection
    map_crs = ccrs.Orthographic(-160, 90)

    # Create the mask editor
    appObj = maskEditor(crs=map_crs, ds=grd.grid['mask'])
    app = appObj.createMaskEditorApp()
    display(app)

The map editor should display after the cell is run.

