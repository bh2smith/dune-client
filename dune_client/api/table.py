"""
Table API endpoints enables users to
create and insert data into Dune.
"""

from __future__ import annotations
from typing import List, Dict, Any

from dune_client.api.base import BaseRouter
from dune_client.models import DuneError


class TableAPI(BaseRouter):
    """
    Implementation of Table endpoints - Plus subscription only
    https://docs.dune.com/api-reference/tables/
    """

    def upload_csv(
        self,
        table_name: str,
        data: str,
        description: str = "",
        is_private: bool = False,
    ) -> bool:
        """
        https://docs.dune.com/api-reference/tables/endpoint/upload
        The write API allows you to upload any .csv file into Dune. The only limitations are:

        - File has to be < 200 MB
        - Column names in the table can't start with a special character or digits.
        - Private uploads require a Plus subscription.

        Below are the specifics of how to work with the API.
        """
        response_json = self._post(
            route="/table/upload/csv",
            params={
                "table_name": table_name,
                "description": description,
                "data": data,
                "is_private": is_private,
            },
        )
        try:
            return bool(response_json["success"])
        except KeyError as err:
            raise DuneError(response_json, "UploadCsvResponse", err) from err

    def create_table(
        self,
        namespace: str,
        table_name: str,
        schema: List[Dict[str, str]],
        description: str = "",
    ) -> Any:
        """
        https://docs.dune.com/api-reference/tables/endpoint/create
        The create table endpoint allows you to create an empty table with a specifc schema in Dune.

        The only limitations are:
        - A table must currently be created as public.
        - If the request tries to create a private table, it will fail.
        - If a table already exists with the same name, the request will fail.
        - Column names in the table can’t start with a special character or a digit.
        """
        payload = {
            "schema": schema,
            "description": description,
        }
        response_json = self._post(
            route=f"/table/{namespace}/{table_name}/create", params=payload
        )
        try:
            return response_json
        except KeyError as err:
            raise DuneError(response_json, "CreateTableResponse", err) from err

    def insert_table(
        self,
        namespace: str,
        table_name: str,
        path: str,
    ) -> Any:
        """
        https://docs.dune.com/api-reference/tables/endpoint/insert
        The insert table endpoint allows you to insert data into an existing table in Dune.

        The only limitations are:
        - The file has to be in json or csv format
        - The file has to have the same schema as the table
        """

        file_extension = path.split(".")[-1]

        with open(path, "rb") as data:
            response_json = self._post(
                route=f"/table/{namespace}/{table_name}/insert",
                headers={
                    "Content-Type": (
                        "text/csv"
                        if file_extension == "csv"
                        else (
                            "application/x-ndjson"
                            if file_extension in ["json", "jsonl"]
                            else None
                        )
                    )
                },
                data=data,
            )
            try:
                return response_json
            except KeyError as err:
                raise DuneError(response_json, "InsertTableResponse", err) from err