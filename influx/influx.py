from influxdb import InfluxDBClient

from database.storage import get_session, init_db


influx_client = InfluxDBClient('172.18.0.2', 8086, 'admin', 'admin', 'drinks')
influx_client.create_database('drinks')

def init_influx():
    pass

def clear_scanevents():
    influx_client.query("delete from drink_scans")

def upload_scanevents():

    session = get_session()

    result = session.execute("""
        SELECT scanevent.id, scanevent.timestamp as time, drink.name, type
        FROM scanevent
        LEFT JOIN drink ON scanevent.barcode = drink.ean
        WHERE scanevent.uploaded_to_influx = FALSE;
    """)

    for scanevent in result:
        id = scanevent['id']
        time = scanevent['time']
        name = scanevent['name']
        type = scanevent['type']

        if name is None:
            continue

        json_body = [
            {
                "measurement": "drink_scans",
                "tags": {
                    "region": "kassel",
                    "type": type,
                    "name": name
                },
                "time": time,
                "fields": {
                    "name": name,
                    "type": type,
                    "value": 1
                }
            }
        ]
        influx_client.write_points(json_body)

        session.execute("""
            UPDATE scanevent
            SET uploaded_to_influx = TRUE
            WHERE id = :id
        """, {"id": id})
        session.commit()

if __name__ == '__main__':
    init_db()
    upload_scanevents()
    #clear_scanevents()