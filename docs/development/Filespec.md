# File specifications

The gridtools library adopts the following file specifications.

The following prefixes are reserved:
 * ds://
 * file://
 * gql://
 * http://
 * https://

## Filenames

A string without a prefix will be assumed to be a local file on a
filesystem.

A file:// prefix will also refer to a file on the local filesystem.

## OpenDAP

A string with the prefix http:// or https:// will be assumed to be
an OpenDAP address supported via the netCDF4 library.

## Data Source

A string with the prefix ds:// will refer to a catalog entry assigned
in the gridtools library.  This may be specified for reading or writing.

## GraphQL

A string with the prefix gql:// will refer to access to a dataset at
a remote server using the GraphQL protocol.  This API is under
consideration for the gridtools library.
