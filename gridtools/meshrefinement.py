'''This was originally GMesh.py from Niki Zahdah.  :cite:p:`Zadeh_2020_ocean_model_topog_generator`

'''
import numpy as np
import pdb

def fourPointAve(x):
    xave = np.copy(x[::2,::2])
    xave[:-1,:-1]=0.25*(x[:-1:2,:-1:2]+x[1::2,1::2]+x[1::2,0:-1:2]+x[0:-1:2,1::2])
    return xave

def is_mesh_uniform(lon,lat):
    """Returns True if the input grid (lon,lat) is uniform and False otherwise"""
    def compare(array):
        eps = np.finfo( array.dtype ).eps # Precision of datatype
        delta = np.abs( array[1:] - array[:-1] ) # Difference along first axis
        error = np.abs( array )
        error = np.maximum( error[1:], error[:-1] ) # Error in difference
        #derror = np.abs( delta - delta.flatten()[0] ) # Tolerance to which comparison can be made
        derror = np.abs( delta - delta.stack(z=(delta.coords)).reset_index('z')[0] )
        #return np.all( derror < ( error + error.flatten()[0] ) )
        return np.all( derror < ( error + error.stack(z=(error.coords)).reset_index('z')[0] ) )
    assert len(lon.shape) == len(lat.shape), "Arguments lon and lat must have the same rank"
    if len(lon.shape)==2: # 2D arralat
        assert lon.shape == lat.shape, "Arguments lon and lat must have the same shape"
    if len(lon.shape)>2 or len(lat.shape)>2:
        raise Exception("Arguments must be either both be 1D or both be 2D arrays")

    #pdb.set_trace()
    return compare(lat) and compare(lon.T)

class MeshRefinement(object):
    """Describes 2D meshes for ESMs.

    Meshes have shape=(nj,ni) cells with (nj+1,ni+1) vertices with coordinates (lon,lat).

    When constructing, either provide 1d or 2d coordinates (lon,lat), or assume a
    uniform spherical grid with 'shape' cells covering the whole sphere with
    longitudes starting at lon0.

    Attributes:

    shape - (nj,ni)
    ni    - number of cells in i-direction (last)
    nj    - number of cells in j-direction (first)
    lon   - longitude of mesh (cell corners), shape (nj+1,ni=1)
    lat   - latitude of mesh (cell corners), shape (nj+1,ni=1)
    area  - area of cells, shape (nj,ni)
    """

    def __init__(self, shape=None, lon=None, lat=None, area=None, lon0=-180., from_cell_center=False, rfl=0):
        """Constructor for Mesh:
        shape - shape of cell array, (nj,ni)
        ni    - number of cells in i-direction (last index)
        nj    - number of cells in j-direction (first index)
        lon   - longitude of mesh (cell corners) (1d or 2d)
        lat   - latitude of mesh (cell corners) (1d or 2d)
        area  - area of cells (2d)
        lon0  - used when generating a spherical grid in absence of (lon,lat)
        rfl   - refining level of this mesh
        """
        if (shape is None) and (lon is None) and (lat is None): raise Exception('Either shape must be specified or both lon and lat')
        if (lon is None) and (lat is not None): raise Exception('Either shape must be specified or both lon and lat')
        if (lon is not None) and (lat is None): raise Exception('Either shape must be specified or both lon and lat')
        # Determine shape
        if shape is not None:
            (nj,ni) = shape
        else: # Determine shape from lon and lat
            if (lon is None) or (lat is None): raise Exception('Either shape must be specified or both lon and lat')
            if len(lon.shape)==1: ni = lon.shape[0]-1
            elif len(lon.shape)==2: ni = lon.shape[1]-1
            else: raise Exception('lon must be 1D or 2D.')
            if len(lat.shape)==1 or len(lat.shape)==2: nj = lat.shape[0]-1
            else: raise Exception('lat must be 1D or 2D.')
        if from_cell_center: # Replace cell center coordinates with cell corner coordinates
            # NOTE: Does not work with 2D lat/lon fields
            ni,nj = ni+1, nj+1
            tmp = np.zeros(ni+1)
            tmp[1:-1] = 0.5 * ( lon[:-1] + lon[1:] )
            tmp[0] = 1.5 * lon[0] - 0.5 * lon[1]
            tmp[-1] = 1.5 * lon[-1] - 0.5 * lon[-2]
            lon = tmp
            tmp = np.zeros(nj+1)
            tmp[1:-1] = 0.5 * ( lat[:-1] + lat[1:] )
            tmp[0] = 1.5 * lat[0] - 0.5 * lat[1]
            tmp[-1] = 1.5 * lat[-1] - 0.5 * lat[-2]
            lat = tmp
        self.ni = ni
        self.nj = nj
        self.shape = (nj,ni)
        # Check shape of arrays and construct 2d coordinates
        if lon is not None and lat is not None:
            if len(lon.shape)==1:
                if len(lat.shape)>1: raise Exception('lon and lat must either be both 1d or both 2d')
                if lon.shape[0] != ni+1: raise Exception('lon has the wrong length')
            if len(lat.shape)==1:
                if len(lon.shape)>1: raise Exception('lon and lat must either be both 1d or both 2d')
                if lat.shape[0] != nj+1: raise Exception('lat has the wrong length')
            if len(lon.shape)==2 and len(lat.shape)==2:
                if lon.shape != lat.shape: raise Exception('lon and lat are 2d and must be the same size')
                if lon.shape != (nj+1,ni+1): raise Exception('lon has the wrong size')
                self.lon = lon
                self.lat = lat
            else:
                self.lon, self.lat = np.meshgrid(lon,lat)
        else: # Construct coordinates
            lon1d = np.linspace(-90.,90.,nj+1)
            lat1d = np.linspace(lon0,lon0+360.,ni+1)
            self.lon, self.lat = np.meshgrid(lon1d,lat1d)
        if area is not None:
            if area.shape != (nj,ni): raise Exception('area has the wrong shape or size')
            self.area = area
        else:
            self.area = None

        self.rfl = rfl #refining level

    def __repr__(self):
        return '<MeshRefinement nj:%i ni:%i shape:(%i,%i)>'%(self.nj,self.ni,self.shape[0],self.shape[1])

    def __getitem__(self, key):
        return getattr(self, key)

    def dump(self):
        """Dump Mesh to tty."""
        print(self)
        print('lon = ',self.lon)
        print('lat = ',self.lat)

    def plot(self, axis, subsample=1, linecolor='k', **kwargs):
        for i in range(0,self.ni+1,subsample):
            axis.plot(self.lon[:,i], self.lat[:,i], linecolor, **kwargs)
        for j in range(0,self.nj+1,subsample):
            axis.plot(self.lon[j,:], self.lat[j,:], linecolor, **kwargs)

    def pcolormesh(self, axis, data, **kwargs):
        return axis.pcolormesh( self.lon, self.lat, data, **kwargs)

    def __lonlat_to_XYZ(lon, lat):
        """Private method. Returns 3d coordinates (X,Y,Z) of spherical coordiantes (lon,lat)."""
        deg2rad = np.pi/180.
        lonr,latr = deg2rad*lon, deg2rad*lat
        return np.cos( latr )*np.cos( lonr ), np.cos( latr )*np.sin( lonr ), np.sin( latr )

    def __XYZ_to_lonlat(X, Y, Z):
        """Private method. Returns spherical coordinates (lon,lat) of 3d coordinates (X,Y,Z)."""
        rad2deg = 180./np.pi
        lat = np.arcsin( Z ) * rad2deg # -90 .. 90
        # Normalize X,Y to unit circle
        sub_roundoff = 2./np.finfo(X[0,0]).max
        R = 1. / ( np.sqrt(X*X + Y*Y) + sub_roundoff )
        lon = np.arccos( R*X ) * rad2deg # 0 .. 180
        lon = np.where( Y>=0, lon, -lon ) # Handle -180 .. 0
        return lon,lat

    def refineby2(self, work_in_3d=True):
        """Returns new Mesh instance with twice the resolution"""

        def local_refine(A):
            """Retruns a refined variable a with shape (2*nj-1,2*ni-1) by linearly interpolation A with shape (nj,ni)."""
            nj,ni = A.shape
            a = np.zeros( (2*nj-1,2*ni-1) )
            a[::2,::2] = A[:,:] # Shared nodes
            a[::2,1::2] = 0.5 * ( A[:,:-1] + A[:,1:] ) # Mid-point along i-direction on original mesh
            a[1::2,::2] = 0.5 * ( A[:-1,:] + A[1:,:] ) # Mid-point along j-direction on original mesh
            a[1::2,1::2] = 0.25 * ( ( A[:-1,:-1] + A[1:,1:] ) + ( A[1:,:-1] + A[:-1,1:] ) ) # Mid-point of cell on original mesh
            return a

        if work_in_3d:
            # Calculate 3d coordinates of nodes (X,Y,Z), Z points along pole, Y=0 at lon=0,180, X=0 at lon=+-90
            X,Y,Z = MeshRefinement.__lonlat_to_XYZ(self.lon, self.lat)

            # Refine mesh in 3d and project onto sphere
            X,Y,Z = local_refine(X), local_refine(Y), local_refine(Z)
            R = 1. / np.sqrt((X*X + Y*Y) + Z*Z)
            X,Y,Z = R*X, R*Y, R*Z

            # Normalize X,Y to unit circle
            #sub_roundoff = 2./np.finfo(X[0,0]).max
            #R = 1. / ( np.sqrt(X*X + Y*Y) + sub_roundoff )
            #X = R * X
            #Y = R * Y

            # Convert from 3d to spherical coordinates
            lon,lat = MeshRefinement.__XYZ_to_lonlat(X, Y, Z)

        else:
            lon,lat = local_refine(self.lon), local_refine(self.lat)

        return MeshRefinement(lon=lon, lat=lat, rfl=self.rfl+1)

    def rotate(self, y_rot=0, z_rot=0):
        """Sequentially apply a rotation about the Y-axis and then the Z-axis."""
        deg2rad = np.pi/180.
        # Calculate 3d coordinates of nodes (X,Y,Z), Z points along pole, Y=0 at lon=0,180, X=0 at lon=+-90
        X,Y,Z = MeshRefinement.__lonlat_to_XYZ(self.lon, self.lat)
        # Rotate anti-clockwise about Y-axis
        C,S = np.cos( deg2rad*y_rot ), np.sin( deg2rad*y_rot )
        X,Z = C*X + S*Z, -S*X + C*Z
        # Rotate anti-clockwise about Y-axis
        C,S = np.cos( deg2rad*z_rot ), np.sin( deg2rad*z_rot )
        X,Y = C*X - S*Y, S*X + C*Y

        # Convert from 3d to spherical coordinates
        self.lon,self.lat = MeshRefinement.__XYZ_to_lonlat(X, Y, Z)

        return self

    def coarsenby2(self, coarser_mesh):
        """Set the height for lower level Mesh by coarsening"""
        if(self.rfl == 0):
            raise Exception('Coarsest grid, no more coarsening possible!')

        coarser_mesh.height = np.copy(self.height[::2,::2])
        coarser_mesh.height[:-1,:-1] = 0.25*(self.height[:-1:2,:-1:2]
                                           + self.height[1::2,1::2]
                                           + self.height[1::2,0:-1:2]
                                           + self.height[0:-1:2,1::2])

        coarser_mesh.h_min = np.copy(self.height[::2,::2])
        coarser_mesh.h_min[:-1,:-1] = np.minimum(self.height[:-1:2,:-1:2],self.height[1::2,1::2])
        coarser_mesh.h_min[:-1,:-1] = np.minimum(coarser_mesh.h_min[:-1,:-1],self.height[1::2,0:-1:2])
        coarser_mesh.h_min[:-1,:-1] = np.minimum(coarser_mesh.h_min[:-1,:-1],self.height[0:-1:2,1::2])

        coarser_mesh.h_max = np.copy(self.height[::2,::2])
        coarser_mesh.h_max[:-1,:-1] = np.maximum(self.height[:-1:2,:-1:2],self.height[1::2,1::2])
        coarser_mesh.h_max[:-1,:-1] = np.maximum(coarser_mesh.h_max[:-1,:-1],self.height[1::2,0:-1:2])
        coarser_mesh.h_max[:-1,:-1] = np.maximum(coarser_mesh.h_max[:-1,:-1],self.height[0:-1:2,1::2])

        coarser_mesh.h_std = np.zeros(coarser_mesh.height.shape)
        coarser_mesh.zm = coarser_mesh.height
        coarser_mesh.xm = fourPointAve(self.xm)
        coarser_mesh.ym = fourPointAve(self.ym)
        coarser_mesh.xxm = fourPointAve(self.xxm)
        coarser_mesh.yym = fourPointAve(self.yym)
        coarser_mesh.xym = fourPointAve(self.xym)
        coarser_mesh.xzm = fourPointAve(self.xzm)
        coarser_mesh.yzm = fourPointAve(self.yzm)

    def mdist(x1,x2):
        """Returns positive distance modulo 360."""
        return np.minimum( np.mod(x1-x2,360.), np.mod(x2-x1,360.) )

    def find_nn_uniform_source(self, lon, lat):
        """Returns the i,j arrays for the indexes of the nearest neighbor point to grid (lon,lat)"""
        assert is_mesh_uniform(lon,lat), 'Grid (lon,lat) is not uniform, this method will not work properly'
        if len(lon.shape)==2:
            # Convert to 1D arrays
            lon,lat = lon[0,:],lat[:,0]
        sni,snj =lon.shape[0],lat.shape[0] # Shape of source
        # Spacing on uniform mesh
        dellon, dellat = (lon[-1]-lon[0])/(sni-1), (lat[-1]-lat[0])/(snj-1)
        # Convert to numbers
        dellon = dellon.data.tolist()
        dellat = dellat.data.tolist()
#original
#        assert self.lat.max()<=lat.max()+0.5*dellat, 'Mesh has latitudes above range of regular grid '+str(self.lat.max())+' '+str(lat.max()+0.5*dellat)
#        assert self.lat.min()>=lat.min()-0.5*dellat, 'Mesh has latitudes below range of regular grid '+str(self.lat.min())+' '+str(lat.min()-0.5*dellat)
#changed
#        assert self.lat.max()>=lat.max()-0.5*dellat, 'Source has latitudes above range of target mesh '+str(self.lat.max())+' '+str(lat.max()-0.5*dellat)
#        assert self.lat.min()<=lat.min()+0.5*dellat, 'Source has latitudes below range of target mesh '+str(self.lat.min())+' '+str(lat.min()+0.5*dellat)
#neither works for bipole

        if abs( (lon[-1]-lon[0])-360 )<=360.*np.finfo( lon.dtype ).eps:
            print("Detected repeated longitude ",lon[0],lon[-1])
            sni-=1 # Account for repeated longitude
        # Nearest integer (the upper one if equidistant)
        #pdb.set_trace()
        #nn_i = np.floor(np.mod(self.lon-lon[0]+0.5*dellon,360)/dellon)
        #nn_j = np.floor(0.5+(self.lat-lat[0])/dellat)
        nn_i = np.floor(np.mod(self.lon-lon[0].data.tolist()+0.5*dellon,360)/dellon)
        nn_j = np.floor(0.5+(self.lat-lat[0].data.tolist())/dellat)
        nn_i = np.minimum(nn_i, sni-1)
        nn_j = np.minimum(nn_j, snj-1)
        nn_i = np.maximum(nn_i, 0)
        nn_j = np.maximum(nn_j, 0)
        assert nn_j.min()>=0, 'Negative j index calculated! j='+str(nn_j.min())
        assert nn_j.max()<snj, 'Out of bounds j index calculated! j='+str(nn_j.max())+'snj='+str(snj)
        assert nn_i.min()>=0, 'Negative i index calculated! i='+str(nn_i.min())
        assert nn_i.max()<sni, 'Out of bounds i index calculated! i='+str(nn_i.max())+'sni='+str(sni)
        return nn_i.astype(int),nn_j.astype(int)

    def source_hits(self, xs, ys, singularity_radius=0.25):
        """Returns an mask array of 1's if a cell with center (xs,ys) is intercepted by a node
           on the mesh, 0 if no node falls in a cell"""
        # Indexes of nearest xs,ys to each node on the mesh
        i,j = self.find_nn_uniform_source(xs,ys)
        sni,snj = xs.shape[0],ys.shape[0] # Shape of source
        hits = np.zeros((snj,sni))
        if singularity_radius>0: hits[np.abs(ys)>90-singularity_radius] = 1
        hits[j,i] = 1
        return hits

    def refine_loop(self, src_lon, src_lat, max_stages=32, max_mb=500, verbose=True, singularity_radius=0.25):
        """Repeatedly refines the mesh until all cells in the source grid are intercepted by mesh nodes.
           Returns a list of the refined meshes starting with parent mesh."""
        Mesh_list, this = [self], self
        hits = this.source_hits(src_lon, src_lat, singularity_radius=singularity_radius)
        nhits, prev_hits, mb = hits.sum().astype(int), 0, 2*8*this.shape[0]*this.shape[1]/1024/1024
        if verbose: print(this, 'Hit', nhits, 'out of', hits.size, 'cells (%.4f'%mb,'Mb)')
        # Conditions to refine
        # 1) Not all cells are intercepted
        # 2) A refinement intercepted more cells
        converged = np.all(hits) or (nhits==prev_hits)
        while(not converged and len(Mesh_list)<max_stages and 4*mb<max_mb):
            this = this.refineby2()
            hits = this.source_hits(src_lon, src_lat, singularity_radius=singularity_radius)
            nhits, prev_hits, mb = hits.sum().astype(int), nhits, 2*8*this.shape[0]*this.shape[1]/1024/1024
            converged = np.all(hits) or (nhits==prev_hits)
            if nhits>prev_hits:
                Mesh_list.append( this )
                if verbose: print(this, 'Hit', nhits, 'out of', hits.size, 'cells (%.4f'%mb,'Mb)')

        if not converged:
            print("Warning: Maximum number of allowed refinements reached without all source cells hit.")

        return Mesh_list

    def sample_source_data_on_target_mesh(self,xs,ys,zs):
        """Returns the array on target mesh with values equal to the nearest-neighbor source point data"""
        # Indexes of nearest xs,ys to each node on the mesh
        i,j = self.find_nn_uniform_source(xs,ys)
        self.height = np.zeros(self.lon.shape)
        #self.height[:,:] = zs[j[:],i[:]]
        self.height[:,:] = zs.data[j[:],i[:]]
        self.h_std = np.zeros(self.lon.shape)
        self.h_min = np.zeros(self.lon.shape)
        self.h_max = np.zeros(self.lon.shape)

	# Quantities needed for calculating the roughness
        self.xm = np.zeros(self.lon.shape)
        self.ym = np.zeros(self.lon.shape)
        self.zm = np.zeros(self.lon.shape)
        self.xxm = np.zeros(self.lon.shape)
        self.yym = np.zeros(self.lon.shape)
        self.xym = np.zeros(self.lon.shape)
        self.xzm = np.zeros(self.lon.shape)
        self.yzm = np.zeros(self.lon.shape)
        #self.xm[:,:] = xs[i[:]]
        self.xm[:,:] = xs.data[i[:]]
        #self.ym[:,:] = ys[j[:]]
        self.ym[:,:] = ys.data[j[:]]
        # We just need a copy here
        #self.zm[:,:] = zs[j[:],i[:]]
        self.zm = self.height.copy()
        self.xxm[:,:] = self.xm[:,:] * self.xm[:,:]
        self.yym[:,:] = self.ym[:,:] * self.ym[:,:]
        self.xym[:,:] = self.xm[:,:] * self.ym[:,:]
        self.xzm[:,:] = self.xm[:,:] * self.zm[:,:]
        self.yzm[:,:] = self.ym[:,:] * self.zm[:,:]

        return

    def least_square_plane_estimate(self, xs,ys,zs):
        """This function returns the estimates for h2 and h and also mean,min,max of the date
           in each grid cell. """
        """It estimates h and h2 passing a least-square plane through the data points in each grid cell."""
        """The plane is calculated via a standard algorithm explained in text books (T. Shifrin, Multivariable Mathematic, p227)"""
        """h2 is estiamted as the standard deviation of z-distance of data points in the grid cell from the fit plane."""
        """h  is estiamted as the value of plane for z calculated at the corner of the grid cell."""

        epsilon=1.0e-5
        #indices of nearest neighbor source point to each target mesh point
        ti,tj = self.find_nn_uniform_source(xs,ys)

        #Initialize with nans as missing values
        #This will leave some mesh point values as nans
        Zmean=np.empty(self.lon.shape)*np.nan
        Zmin =np.empty(self.lon.shape)*np.nan
        Zmax =np.empty(self.lon.shape)*np.nan
        Zstd =np.empty(self.lon.shape)*np.nan

        #Loop over each grid cell. Is there a numpy way of doing this?
        dlon=np.roll(self.lon,shift=-1,axis=1)-self.lon
        dlat=np.roll(self.lat,shift=-1,axis=0)-self.lat
        dti =np.roll(ti,shift=-1,axis=1)-ti
        dtj =np.roll(tj,shift=-1,axis=0)-tj
        #fix the last elements #halo?
        dlon[:,-1]=dlon[:,-2]
        dlat[-1,:]=dlat[-2,:]
        dti[:,-1]=dti[:,-2]
        #print(dtj)
        dtj[-1,:]=dtj[-2,:]
        #print(dtj)
        for J in range(0,self.lat.shape[0]):
            for I in range(0,self.lon.shape[1]):
                #Initialize to the NN source value. Reasonable?
                znn=zs[tj[J,I],ti[J,I]]
                Zmean[J,I]= znn
                Zmin[J,I] = znn
                Zmax[J,I] = znn
                Zstd[J,I] = 0.0

                #bounds of a target cell
                lon_min=self.lon[J,I]
                lon_max=lon_min+dlon[J,I]
                lat_min=self.lat[J,I]
                lat_max=lat_min+dlat[J,I]
                #bounds of indexes of NN source cell
                tj_min=tj[J,I]
                tj_max=tj_min+dtj[J,I]
                ti_min=ti[J,I]
                ti_max=ti_min+dti[J,I]
                ti_max=min(ti_max,xs.shape[0]-1)
                tj_max=min(tj_max,ys.shape[0]-1)
                #We don't know how many data points are in each grid cell. Let's say it's M.
                #According to the algorithm, we need to create
                X=[]
                Y=[]
                Z=[]
                #print('J,I ',J,I)
                #print(lon_min,lon_max)
                #print(ti_min,ti_max)
                #print(lat_min,lat_max)
                #print(tj_min,tj_max,dtj[J,I])
                for jj in range(tj_min,tj_max+1):
                    #print(ys[jj],lat_min,lat_max)
                    if((ys[jj]>=lat_min) and (ys[jj]<lat_max)):
                        for ii in range(ti_min,ti_max+1):
                            if(xs[ii] >= lon_min and xs[ii] < lon_max):
                                #print('jj,ii',jj,ii)
                                X.append(np.array(xs[ii]))
                                Y.append(np.array(ys[jj]))
                                Z.append(np.array(zs[jj,ii]))
                #print(len(Z))
                if(len(Z)==0):
                    continue
                #cast these in numpy arrays
                X = np.asarray(X)
                Y = np.asarray(Y)
                Z = np.asarray(Z)
                #The algorithm fits a plane z=P(x,y) by minimizing \sum_i (z_i - P(x_i,y_i))
                #It shows that
                #1. P is of the form P = zm + ax*(x-xm) + ay*(y-ym),
                #                    xm,ym,zm being the means of data x_i,y_i,z_i respectively
                #     I.e., the least square plane passes through the point (xm,ym,zm)
                #2. It gives the following formula for ax and ay (solution of 2by2 linear system)

                N=X.size
                xm=np.sum(X)/N
                ym=np.sum(Y)/N
                zm=np.sum(Z)/N
                sxx=np.dot(X-xm,X-xm)#/N
                syy=np.dot(Y-ym,Y-ym)#/N
                sxy=np.dot(X-xm,Y-ym)#/N
                syz=np.dot(Y-ym,Z-zm)#/N
                sxz=np.dot(X-xm,Z-zm)#/N

                det=(sxx*syy-sxy*sxy)
                if(abs(det) < epsilon): #No solutions
                    continue
                ax=(sxz*syy-syz*sxy)/det
                ay=(syz*sxx-sxz*sxy)/det
                d=Z-zm - ax*(X-xm) - ay*(Y-ym)

                Zstd[J,I]=d.std()
                #Zij[J,I] = zm + ax*(self.lon[J,I]-xm)+ay*(self.lat[J,I]-ym) #corner fit value
                Zmean[J,I]= zm
                Zmin[J,I] = Z.min()
                Zmax[J,I] = Z.max()

                #Check: The sum of Distances must be very small, almost zero
                #assert abs(d.sum())<0.00001, "Bad fit: The sum of Distances is large at "+str(I)+","+str(J)+" = "+str(d.sum())+" compared to min  "+str(Zmin[J,I])
                if(abs(d.sum())>epsilon):
                    print("Bad fit: The sum of Distances is large at ("+str(I)+","+str(J)+") = "+str(d.sum())+" compared to min  "+str(Zmin[J,I]))

        return Zstd,Zmean,Zmin,Zmax


