# Test imports using
#   import * syntax
def test_import():
    try:
        import gridtools
        assert "gridtools" == "gridtools"
    except:
        assert "failed import" == "gridutils"
