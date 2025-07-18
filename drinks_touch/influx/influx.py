from influxdb import InfluxDBClient

from database.storage import Session, with_db

influx_client = InfluxDBClient("172.18.0.2", 8086, "admin", "admin", "drinks")
influx_client.create_database("drinks")


def init_influx():
    pass


def clear_scanevents():
    influx_client.query("delete from drink_scans")


@with_db
def upload_scanevents():
    result = Session().execute(
        """
        SELECT scanevent.id, scanevent.timestamp as time, drink.name, type
        FROM scanevent
        LEFT JOIN drink ON scanevent.barcode = drink.ean
        WHERE scanevent.uploaded_to_influx = FALSE;
    """
    )

    for scanevent in result:
        scan_id = scanevent["id"]
        scan_time = scanevent["time"]
        scan_name = scanevent["name"]
        scan_type = scanevent["type"]

        if scan_name is None:
            continue

        json_body = [
            {
                "measurement": "drink_scans",
                "tags": {"region": "kassel", "type": scan_type, "name": scan_name},
                "time": scan_time,
                "fields": {"name": scan_name, "type": scan_type, "value": 1},
            }
        ]
        influx_client.write_points(json_body)

        Session().execute(
            """
            UPDATE scanevent
            SET uploaded_to_influx = TRUE
            WHERE id = :id
        """,
            {"id": scan_id},
        )


if __name__ == "__main__":
    upload_scanevents()
    # clear_scanevents()
