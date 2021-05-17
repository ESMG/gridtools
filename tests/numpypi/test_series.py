from __future__ import print_function

import hashlib
import numpypi.numpypi_series as numpy  # Module to test

def logistic_map(x, r=4.-1./32):
    """Logistic map r*x*(1-x)"""
    return r * x * ( 1. - x )
def generate_numbers(n, r=4.-1./32, x0=0.5, n0=0):
    """Generates reproducible vector of values between 0 and 1"""
    for k in range(n0):
        x0 = logistic_map( x0, r=r)
    x = numpy.zeros(n)
    x[0] = x0
    for k in range(1,n):
        x[k] = logistic_map( x[k-1], r=r)
    return x
def compare_numbers(x, y, good_hash=None, quiet=False):
    # Compare hashes
    status = True
    # Numerical test
    error = ( x - y )
    n = numpy.count_nonzero( error )
    if n>0:
        if not quiet: print(' X There were %i differences detected (out of %i) or %3.4f%% hits.'%(n,error.size,(100.*n)/error.size))
        k = numpy.nonzero( error )[0]
        if not quiet: print('   First few values ...')
        frac = error / x
        for j in range( min(n, 5) ):
            i = k[j]
            a,b,e,f = x[i],y[i],error[i],frac[i]
            if not quiet: print('      x(%i)=%23.15e y(%i)=%23.15e error=%.5e frac. err.=%.2e'%(i,a,i,b,e,f))
        print('   Largest fractional error = %.2e'%numpy.abs( frac ).max() )
        status = False
    # Bitwise (hash) test
    hx = hashlib.sha256( numpy.array( x ) ).hexdigest()
    hy = hashlib.sha256( numpy.array( y ) ).hexdigest()
    print('   hash(x) =', hx, 'min=%.15e max=%.15e'%(x.min(), x.max()))
    if hx != hy and status:
        print('   hash(y) =', hy, 'min=%.15e max=%.15e'%(y.min(), y.max()))
        print(' X Hashes do not match (i.e. bits differ).')
        status = False
    # Recorded hash
    if good_hash is not None:
        if hx == good_hash:
            print('   Hash matches recorded hash.')
        else:
            print('   hash(R) =', good_hash)
            print(' X Hash does NOT match recorded hash!')
            status = False
    return status
def writefile(filename, vals):
    f = netCDF4.Dataset(filename, 'w', clobber=True, format='NETCDF3_CLASSIC')
    v = f.createDimension('n', len(vals) )
    v = f.createVariable('results', 'f8', ('n',))
    v[:] = numpy.array(vals)[:]
    f.close()

N = 1024*1024
x01 = generate_numbers(N, r=4.-1./(1024*1024*1024*1024)) # Reproducible numbers between 0..1

print('Generated test numbers: ', end='')
for k in range(4): print( '%.15e'%x01[k], end=', ' )
print('...')
x01_hash = 'e6eb0684e329098c7c3fd2514e14436d27dfc13395237b179168ec34030e0c11'
assert compare_numbers(x01, x01, good_hash=x01_hash), 'Generated test numbers did not reproduce!'

# Generate better numbers
x01 = generate_numbers(N, r=4.-1./(1024*1024*1024*1024), n0=987654) # Reproducible numbers between 0..1
print('Generated test numbers: ', end='')
for k in range(4): print( '%.15e'%x01[k], end=', ' )
print('...')
x01_hash = 'b0e634899b6519687c044e0310b2ac9bf0e56704dcd70696749a9b84da2e3661'
assert compare_numbers(x01, x01, good_hash=x01_hash), 'Generated test numbers did not reproduce!'

# Floating point range

print('Check that maximum floating point number (numpy.finfo.max) is bitwise as expected')
x = numpy.array([numpy.finfo(float).max])
max_hash = 'dd46fdd197731f40f29d789fd02be525b10ff16ea3b7830c9f2c5b28131420ff'
assert compare_numbers(x, x, good_hash=max_hash), 'numpy.finfo.mas did not reproduce'

print('Check that floating point epsilon (numpy.finfo.eps) is bitwise as expected')
x = numpy.array([numpy.finfo(float).eps])
max_hash = '78902dbbf3ee23e635e0b63fd65aea1e80d4a8b08559ea0bb884c7eb872e15d8'
assert compare_numbers(x, x, good_hash=max_hash), 'numpy.finfo.eps did not reproduce'

# sqrt()

print('Check sqrt() for range 0 .. 1')
x = numpy.sqrt( x01  )
sqrt_hash = 'cb46fde585dc617517938e5ff545ed2cb35bf042c0aa7f48ed14ab02d003106e'
assert compare_numbers(x, x, good_hash=sqrt_hash), 'numpypi intrinsic sqrt() failed to reproduce recorded hash!'

print('Check sqrt() for large numbers')
x = numpy.sqrt( x01 * numpy.finfo(float).max  )
sqrt_hash = '388bbf35441a36db561fb4b46d726d03a4dd7e5316f87218f876f0a4b07fc8a2'
assert compare_numbers(x, x, good_hash=sqrt_hash), 'numpypi intrinsic sqrt() failed to reproduce recorded hash!'

# Special values

print('Check that PI (numpy.pi) is bitwise as expected')
x = numpy.array([numpy.pi])
pi_hash = '8b5319c77d1df2dcfcc3c1d94ab549a29d2b8b9f61372dc803146cbb1d2800b9'
assert compare_numbers(x, x, good_hash=pi_hash), 'numpy.pi did not reproduce'

print('Check numpy intrinsics for special values')
x = numpy.array([ numpy.sin([numpy.pi/4]), numpy.cos([numpy.pi/4]), numpy.tan(numpy.array([numpy.pi/4])) ])
y = numpy.array([ numpy.sqrt([2])/2, numpy.sqrt([2])/2,  1.0 ])
assert not compare_numbers(x, y, quiet=True), 'numpy intrinsics unexpectedly matched!'

# Ranges to test direct series

print('Check numpypi intrinsic sin() for range +/- pi/4')
x = numpy.sin( (x01 - 0.5)*numpy.pi*0.5 )
sin_hash = '8ce99db1746bd61d93f9f94bf0bb0f1df8e8dc07ff9090cde35be4626b37a33d'
assert compare_numbers(x, x, good_hash=sin_hash), 'numpypi intrinsic sin() failed to reproduce recorded hash!'

print('Check numpypi intrinsic cos() for range +/- pi/4')
x = numpy.cos( (x01 - 0.5)*numpy.pi*0.5 )
cos_hash = '5a2c8c1cda314147ba3a5dbbb4746d6530946c1f880be2943900d069d94bce31'
assert compare_numbers(x, x, good_hash=cos_hash), 'numpypi intrinsic cos() failed to reproduce recorded hash!'

print('Check numpypi intrinsic tan() for range +/- pi/8')
x = numpy.tan( (x01 - 0.5)*numpy.pi*0.25 )
tan_hash = '53a7c0e6b160508b0b3828684514c9f832f5d294633263e776310b3f352e7d55'
assert compare_numbers(x, x, good_hash=tan_hash), 'numpypi intrinsic tan() failed to reproduce recorded hash!'

# Range +/- pi/2

print('Check numpypi intrinsic sin() for range +/- pi/2')
x = numpy.sin( (x01 - 0.5)*numpy.pi )
sin_hash = '97559ae4443b70b770bdc3bcc9d598cb3685f6498ffe1c6f0e8156f925bd3f1c'
assert compare_numbers(x, x, good_hash=sin_hash), 'numpypi intrinsic sin() failed to reproduce recorded hash!'
#assert x.min() >= -1., 'numpypi sin(x)<-1 !'
#assert x.max() <= 1., 'numpypi sin(x)<-1 !'

print('Check numpypi intrinsic cos() for range +/- pi/2')
x = numpy.cos( (x01 - 0.5)*numpy.pi )
cos_hash = 'f6bbd009835c91e6ace615b1b1184971c587d0924f0e768976742472a8fe576f'
assert compare_numbers(x, x, good_hash=cos_hash), 'numpypi intrinsic cos() failed to reproduce recorded hash!'
#assert x.min() >= -1., 'numpypi cos(x)<-1 !'
#assert x.max() <= 1., 'numpypi cos(x)<-1 !'

print('Check numpypi intrinsic tan() for range +/- pi/2')
x = numpy.tan( (x01 - 0.5)*numpy.pi )
tan_hash = '3270afefda0d569d6e349a94816fe252b077322b19c042dfc363f12555df45d8'
assert compare_numbers(x, x, good_hash=tan_hash), 'numpypi intrinsic tan() failed to reproduce recorded hash!'

print('Check numpypi intrinsic arcsin() for range +/ 3/4')
x = numpy.arcsin( ( x01 - 1. ) * 1.5 )
arcsin_hash = '72374df70534b71783f5eb19867ff1a30894a53e83775e594672487ace6888c0'
assert compare_numbers(x, x, good_hash=arcsin_hash), 'numpypi intrinsic arcsin() failed to reproduce recorded hash!'

print('Check numpypi intrinsic arcsin() for range +/- 1')
x = numpy.arcsin( 2.*x01 - 1. )
arcsin_hash = 'd0d329c09f4f7801b05a65c172b9895f272e61e6a3aca38eb6549acaf3289fd8'
assert compare_numbers(x, x, good_hash=arcsin_hash), 'numpypi intrinsic arcsin() failed to reproduce recorded hash!'

#print('Check numpypi intrinsic arccos() for range of values')
#x = numpy.arccos( 2.*x01 - 1. )
#arccos_hash = '2db2ba8daaa85a5365cd0ae6b8bb90749f4fc29b61ffb8a9d0ca959b47014787'
#assert compare_numbers(x, x, good_hash=arccos_hash), 'numpypi intrinsic arccos() failed to reproduce recorded hash!'

print('Check numpypi intrinsic arctan()')
x = numpy.arctan( 2.*x01 - 1. )
arctan_hash = '2ffdcdc64dff4b8c8710eb204b422c8d965fcba6d96aebe868934959aab057aa'
assert compare_numbers(x, x, good_hash=arctan_hash), 'numpypi intrinsic arctan() failed to reproduce recorded hash!'

print('Check numpypi intrinsic arctan2()')
a = numpy.pi * ( 2.*x01 - 1. ) # -pi .. pi
x,y = numpy.cos( a ), numpy.sin( a )
t = numpy.arctan2(y,x)
arctan2_hash = '1da506787584e9f7140347de5d127356f6d547bf4b0a65feec03278a477805e1'
assert compare_numbers(t, t, good_hash=arctan2_hash), 'numpypi intrinsic arctan2() failed to reproduce recorded hash!'
