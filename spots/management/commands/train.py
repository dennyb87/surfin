import pickle
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from spots.analytics.domain import SpotSnapshotTimeserieV1
from spots.models import Spot as SpotModel


class Command(BaseCommand):
    help = """Train models"""

    def add_arguments(self, parser):
        parser.add_argument("--store", type=int, default=0)

    def handle(self, *args, **options):
        spot = SpotModel.objects.first()
        timeserie = SpotSnapshotTimeserieV1.build_for_spot(spot)
        df = pd.DataFrame(snapshot.to_dict() for snapshot in timeserie)
        df.set_index(["created"], inplace=True)
        df.sort_values(by=["created"], inplace=True, ascending=False)
        df.drop(columns=["id"], inplace=True)

        # Separate features and target variable
        X = df.drop(columns=["wave_size_score"])
        y = df["wave_size_score"]

        # Split into training and testing datasets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train a Random Forest Regressor
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train)

        # Predict on the test set
        y_pred = model.predict(X_test)

        # Evaluate the model
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        self.stdout.write(self.style.SUCCESS(f"Root Mean Squared Error: {rmse}"))

        store = bool(options.get("store", 0))
        if store:
            with open("spot_model.pkl", "wb") as file:
                pickle.dump(model, file)
