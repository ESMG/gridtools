# Test imports using
#   from * import * syntax

def test_from_import():
    try:
        from gridtools.gridutils import GridUtils
        assert "gridtools.gridutils" == "gridtools.gridutils"
    except:
        assert "failed import" == "gridtools.gridutils"

    try:
        from gridtools.sysinfo import SysInfo
        assert "gridtools.sysinfo" == "gridtools.sysinfo"
    except:
        assert "failed import" == "gridtools.sysinfo"

    try:
        grd = GridUtils()
        assert "grd" == "grd"
    except:
        assert "failed" == "Unable to create GridUtils() object"

    # Test application loading
    try:
        dashboard = grd.app()
        assert "dashboard" == "dashboard"
    except:
        assert "failed" == "Unable to create application object"
