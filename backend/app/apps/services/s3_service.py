import asyncio
from contextlib import asynccontextmanager
from uuid import UUID

import aioboto3
from fastapi import UploadFile
from settings import settings


class S3Storage:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET
        self.session = aioboto3.Session()

    @asynccontextmanager
    async def get_s3_client(self):
        async with self.session.client(
            service_name="s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        ) as s3_client:
            yield s3_client

    async def upload_files(
        self,
        files: list[UploadFile] | UploadFile,
        uuid_obj: UUID | str,
        root_dir: str = "productImages",
        is_needed_bucket_name_in_url: bool = False,
    ):
        print(settings.S3_ENDPOINT)
        if isinstance(files, UploadFile):
            files = [files]

        tasks = []
        urls = []

        async with self.get_s3_client() as s3_client:
            for file in files:
                file.file.seek(0)
                object_name = f"{root_dir}/{str(uuid_obj)}/{file.filename}"
                tasks.append(
                    s3_client.upload_fileobj(file.file, self.bucket_name, object_name)
                )
                if is_needed_bucket_name_in_url:
                    urls.append(
                        f"{settings.S3_PUBLIC_URL}/{self.bucket_name}/{object_name}",
                    )
                else:
                    urls.append(
                        f"{settings.S3_PUBLIC_URL}/{object_name}",
                    )
            await asyncio.gather(*tasks)
            return urls


s3_storage = S3Storage()
