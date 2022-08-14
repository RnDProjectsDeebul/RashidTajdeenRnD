Feature: Red-drone at distance 5-30 meters


Scenario: Correct drone at correct distance
	Given we have generated images of red drone at varying distance 2-50 meters
	When we predict the distance of the generated images with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be less than 0.15

Scenario: Correct drone at distance less than expected
	Given we have generated images of red drone at varying distance 0-2 meters
	When we predict the distance of the generated images with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Correct drone at distance higher than expected
	Given we have generated images of red drone at varying distance 50-100 meters
	When we predict the distance of the generated images with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Different drone at correct distance
	Given we have generated images of black drone at varying distance 2-50 meters
	When we predict the distance of the generated images with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Correct drone at correct distance with additional correct drone
	Given we have generated images of red drone at varying distance 5-30 meters, and additional red drone
	When we predict the distance of the generated images with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15