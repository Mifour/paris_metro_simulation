import json
import sys
from csv import DictReader
from dataclasses import dataclass, is_dataclass, asdict
from datetime import date
from math import asinh, degrees, radians, tan
from typing import Self, Union

# resolution
width = 2048.0
height = 2048.0
padding = 32.0

# colors of metro lines
line_colors = {
    "3B": "98D4E2",
    "7B": "83C491",
    "1": "FFCE00",
    "2": "0064B0",
    "3": "9F9825",
    "4": "C04191",
    "5": "F28E42",
    "6": "83C491",
    "7": "F3A4BA",
    "8": "CEADD2",
    "9": "D5C900",
    "10": "E3B32A",
    "11": "764C28",
    "12": "007852",
    "13": "6C90B4",
    "14": "62259D",
}


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class FromCSV:
    @classmethod
    def from_csv(cls, dico: dict) -> Self:
        return cls(
            **{
                k: cls.__dataclass_fields__[k].type(v)  # type: ignore
                for k, v in dico.items()
                if k in cls.__dataclass_fields__  # type: ignore
            }
        )


@dataclass
class Calendar(FromCSV):
    service_id: str
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int
    start_date: str
    end_date: str


@dataclass
class CalendarDate(FromCSV):
    service_id: str
    date: int
    exception_type: int


@dataclass
class Route(FromCSV):
    route_id: str
    agency_id: str
    route_short_name: str
    route_type: int


@dataclass
class Trip(FromCSV):
    route_id: str
    service_id: str
    trip_id: str
    trip_headsign: str
    direction_id: int


@dataclass
class Stop(FromCSV):
    stop_id: str
    stop_name: str
    stop_lon: float
    stop_lat: float


@dataclass
class StopTime(FromCSV):
    trip_id: str
    arrival_time: str
    departure_time: str
    stop_id: str
    stop_sequence: int


@dataclass
class Bounds(FromCSV):
    min_x: float
    max_x: float
    min_y: float
    max_y: float


@dataclass
class Station(FromCSV):
    id: int
    name: str
    x: float
    y: float


@dataclass
class Line(FromCSV):
    id: str
    name: str
    color: str


@dataclass
class Keyframe(FromCSV):
    station: int
    arrival: int
    departure: int


@dataclass
class Train(FromCSV):
    id: str
    line: str
    direction: int
    headsign: str
    keyframes: list[Keyframe]


@dataclass
class Dataset(FromCSV):
    version: int
    bounds: Bounds
    date: str
    stations: list[Station]
    lines: list[Line]
    trains: list[Train]


def read_csv(path: str):
    with open(path) as file:
        content = list(DictReader(file))
    return content


def date_as_yyyymmdd(_date: date) -> int:
    return int(_date.strftime("%Y%m%d"))


def parse_gtfs_time(value: str) -> int:
    # GTFS allows hours >= 24
    hours, minutes, _seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + int(_seconds)


def is_service_active(calendar: Calendar, _date: date) -> bool:
    yyyymmdd = str(date_as_yyyymmdd(_date))
    if not calendar.start_date <= yyyymmdd <= calendar.end_date:
        return False

    match _date.isoweekday():
        case 1:
            return calendar.monday == 1
        case 2:
            return calendar.tuesday == 1
        case 3:
            return calendar.wednesday == 1
        case 4:
            return calendar.thursday == 1
        case 5:
            return calendar.friday == 1
        case 6:
            return calendar.saturday == 1
        case 7:
            return calendar.sunday == 1
        case _:
            raise ValueError(f"is_service_active received: {calendar}")


def project(lon: float, lat: float) -> tuple[float, float]:
    # Mercator lon & lat to local 2D space
    return (lon, -(degrees(asinh(tan(radians(lat))))))


def main():
    args = sys.argv
    if len(args) != 4:
        raise ValueError("usage: <gtfs-directory> <YYYY-MM-DD> <output.json>")
    _, gtfs_dir, _date, output = args
    _date = date.fromisoformat(_date)

    print(f"{gtfs_dir=}")
    print(f"{_date=}")
    print(f"{output=}")
    routes = [Route.from_csv(x) for x in read_csv(gtfs_dir + "routes.txt")]
    trips = [Trip.from_csv(x) for x in read_csv(gtfs_dir + "trips.txt")]
    stops = [Stop.from_csv(x) for x in read_csv(gtfs_dir + "stops.txt")]
    stop_times = [StopTime.from_csv(x) for x in read_csv(gtfs_dir + "stop_times.txt")]
    calendars = [Calendar.from_csv(x) for x in read_csv(gtfs_dir + "calendar.txt")]
    calendar_dates = [
        CalendarDate.from_csv(x) for x in read_csv(gtfs_dir + "calendar_dates.txt")
    ]
    date_id = date_as_yyyymmdd(_date)
    active_services = {
        cal.service_id for cal in calendars if is_service_active(cal, _date)
    }

    # gtfs exception
    for excep in calendar_dates:
        if excep.date != date_id:
            continue
        match excep.exception_type:
            case 1:
                active_services.add(excep.service_id)  # service added
            case 2:
                active_services.remove(excep.service_id)  # service removed

    # IDFM route_type 1 = metro
    # potentially can add other networks of transportation
    metro_routes = {
        route.route_id: route.route_short_name
        for route in routes
        if route.route_type == 1 and route.agency_id == "IDFM:Operator_100"  # ratp
    }

    metro_trips = [
        trip
        for trip in trips
        if trip.service_id in active_services and trip.route_id in metro_routes
    ]

    active_trips_ids = {trip.trip_id for trip in metro_trips}

    station_ids = {
        stop_time.stop_id
        for stop_time in stop_times
        if stop_time.trip_id in active_trips_ids
    }

    stops_by_ids = {stop.stop_id: stop for stop in stops}

    projected_stations = []
    min_x, min_y, max_x, max_y = (
        float("inf"),
        float("inf"),
        float("-inf"),
        float("-inf"),
    )
    for stop_id in station_ids:
        stop = stops_by_ids.get(stop_id)
        if stop is None:
            continue
        x, y = project(stop.stop_lon, stop.stop_lat)
        projected_stations.append((stop_id, stop.stop_name, x, y))
        min_x = min(x, min_x)
        min_y = min(y, min_y)
        max_x = max(x, max_x)
        max_y = max(y, max_y)

    scale_x = (width - 2.0 * padding) / (max_x - min_x)
    scale_y = (height - 2.0 * padding) / (max_y - min_y)
    scale = min(scale_x, scale_y)

    station_id_map = {}
    output_stations = []

    for index, (stop_id, name, x, y) in enumerate(projected_stations):
        # positions in the local 2D space
        px = padding + (x - min_x) * scale
        py = padding + (y - min_y) * scale

        station_id_map[stop_id] = index
        output_stations.append(Station(id=index, name=name, x=px, y=py))

    trip_stop_times = {}
    for stop_time in stop_times:
        if stop_time.trip_id not in active_trips_ids:
            continue
        trip_stop_times.setdefault(stop_time.trip_id, []).append(stop_time)

    for times in trip_stop_times.values():
        times.sort(key=lambda time: time.stop_sequence)

    output_trains = []
    for trip in metro_trips:
        route_name = metro_routes[trip.route_id]
        times = trip_stop_times[trip.trip_id]
        keyframes = []
        for stop_time in times:
            station = station_id_map.get(stop_time.stop_id)
            if station is None:
                continue
            arrival = parse_gtfs_time(stop_time.arrival_time)
            departure = parse_gtfs_time(stop_time.departure_time)
            keyframes.append(Keyframe(station, arrival, departure))
        if len(keyframes) < 2:
            continue
        output_trains.append(
            Train(
                id=trip.trip_id,
                line=route_name,
                direction=trip.direction_id,
                headsign=trip.trip_headsign,
                keyframes=keyframes,
            )
        )

    lines = sorted(
        [
            Line(id=name, name=name, color=line_colors[name])
            for name in metro_routes.values()
        ],
        key=lambda line: line.name,
    )

    dataset = Dataset(
        version=1,
        bounds=Bounds(min_x=0.0, max_x=width, min_y=0.0, max_y=height),
        date=_date.isoformat(),
        stations=output_stations,
        lines=lines,
        trains=output_trains,
    )

    print(f"Output stations : {len(dataset.stations)}")
    print(f"Output lines    : {len(dataset.lines)}")
    print(f"Output trains   : {len(dataset.trains)}")

    with open(output, "w") as file:
        json.dump(dataset, file, cls=EnhancedJSONEncoder)

    print("Done !")


main()
