Feature: Red-drone at distance 5-30 meters


Scenario: Correct drone at correct distance
    Given the scenario has red drone
    And the varying distance is 2-50 meters
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be less than 0.15

Scenario: Correct drone at distance less than expected
    Given the scenario has red drone
    And the varying distance is 0-2 meters
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Correct drone at distance higher than expected
    Given the scenario has red drone
    And the varying distance is 50-100 meters
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Different drone at correct distance
    Given the scenario has black drone
    And the varying distance is 2-50 meters
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Correct drone at correct distance with additional correct drone
    Given the scenario has red drone
    And the scenario has an additional red drone
    And the varying distance is 2-50 meters
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Correct drone at correct distance with camera out-of-focus
    Given the scenario has red drone
    And the varying distance is 2-50 meters
    And the camera is out-of-focus
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15

Scenario: Correct drone at correct distance at night
    Given the scenario has red drone
    And the varying distance is 2-50 meters
    And the environment is night
	When we have images for the scenario
	And we predict the distance with the model trained on red drone from 2-50 meters
	Then the rmse loss is expected to be higher than 0.15