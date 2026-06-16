import pynapple as nap
from pynwb import NWBHDF5IO
from dandi.dandiapi import DandiAPIClient
import fsspec
from fsspec.implementations.cached import CachingFileSystem
import h5py

dandiset_id, filepath = (
    "000939",
    "sub-A3702/sub-A3702_ses-191126_behavior+ecephys.nwb",
)


def stream_dandiset(dandiset_id, filepath):
    with DandiAPIClient() as client:
        asset = client.get_dandiset(dandiset_id, "draft").get_asset_by_path(filepath)
        s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)

    # first, create a virtual filesystem based on the http protocol
    fs = fsspec.filesystem("http")

    # create a cache to save downloaded data to disk (optional)
    fs = CachingFileSystem(
        fs=fs,
        cache_storage="nwb-cache",  # Local folder for the cache
    )

    # next, open the file
    file = h5py.File(fs.open(s3_url, "rb"))
    io = NWBHDF5IO(file=file, load_namespaces=True)

    return nap.NWBFile(io.read())


nwbfile = stream_dandiset(dandiset_id, filepath)
