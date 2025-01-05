from unittest.mock import patch

import responses
from django.test import TestCase

from cftoscana.tests.factories import CFTBuoyStationFactory
from ipcamlive.tests.factories import IPCamLiveWebcamFactory
from spots.domain import SpotDomain, SpotSetDomain, SpotSnapshotDomain
from spots.models import SpotSnapshot
from spots.tests.factories import SpotFactory
from windy.tests.factories import WindyWebcamFactory


class SpotSetTakeSnapshotsTestCase(TestCase):
    def setUp(self):
        self.spot_orm = SpotFactory()
        self.spot = SpotDomain.from_orm_obj(self.spot_orm)
        self.windy_webcam_orm = WindyWebcamFactory(spot=self.spot_orm)
        self.ipcamlive_webcam_orm = IPCamLiveWebcamFactory(spot=self.spot_orm)
        self.buoy_station_orm = CFTBuoyStationFactory()
        self.buoy_station_orm.spots.add(self.spot_orm)

        self.spots = SpotSetDomain([self.spot])

        self.ipcamlive_screenshot_uri = f"https://ipcamlive.com/player/snapshot.php?alias={self.ipcamlive_webcam_orm.alias}"
        self.windy_preview_uri = "https://api.windy.com/webcams/lovely_preview_uri.jpg"
        self.windy_resp = {
            "total": 1,
            "webcams": [
                {
                    "title": "my lovely webcam",
                    "viewCount": 118484,
                    "webcamId": self.windy_webcam_orm.windy_uid,
                    "status": "active",
                    "lastUpdatedOn": "2024-04-20T16:04:09.000Z",
                    "images": {"current": {"preview": self.windy_preview_uri}},
                }
            ],
        }

        self.meteonetwork_resp = {
            "lat": "45.5125000007195",
            "lon": "9.312499993800508",
            "temperature": "11.0",
            "rh": "79",
            "dew_point": "7.1",
            "daily_rain": "25.1",
            "smlp": "1024.7",
            "wind_direction": "179",
            "wind_direction_cardinal": "S",
            "wind_speed": "2.4",
            "distance": "1.7",
            "place": None,
            "name": None,
            "current_tmin": None,
            "current_tmed": None,
            "current_tmax": None,
            "current_rhmin": None,
            "current_rhmed": None,
            "current_rhmax": None,
            "current_wgustmax": None,
            "current_wspeedmax": None,
            "current_wspeedmed": None,
            "current_uvmed": None,
            "current_uvmax": None,
            "current_radmed": None,
            "current_radmax": None,
        }

    @patch("cftoscana.domain.CFTBuoyDataExtractor.get_station_data")
    def test_success(self, mock_get_station_data):
        snapshots = SpotSnapshot.objects.all()
        self.assertEqual(snapshots.count(), 0)
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                "GET",
                f"https://api.windy.com/webcams/api/v3/webcams?limit=10&offset=0&webcamIds={self.windy_webcam_orm.windy_uid}&include=images",
                json=self.windy_resp,
                status=200,
            )
            rsps.add(
                "GET",
                self.windy_preview_uri,
                body="dummy_windy_webcam_preview_payload",
                status=200,
            )
            rsps.add(
                "GET",
                f"https://api.meteonetwork.it/v3/interpolated-realtime/?lat={self.spot.lat}&lon={self.spot.lon}",
                json=self.meteonetwork_resp,
                status=200,
            )
            rsps.add(
                "GET",
                self.ipcamlive_screenshot_uri,
                body="dummy_ipcamlive_webcam_screenshot_payload",
                status=200,
            )
            mock_get_station_data.return_value = {"x": [0, 1, 2], "y": [0, 1, 2]}

            data = self.spots.take_snapshots()

        self.assertEqual(snapshots.all().count(), 1)
        self.assertEqual(len(data), 1)
        self.assertEqual(mock_get_station_data.call_count, 3)

        snapshot_orm = SpotSnapshot.objects.get(id=data[0].pk)
        snapshot = SpotSnapshotDomain.from_orm_obj(snapshot_orm)

        self.assertEqual(data, [snapshot])
