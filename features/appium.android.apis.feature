Feature: Appium.android.apis

  @bdd @smoke
  Scenario: Launch
    Given app is opened
    Then package should be "io.appium.android.apis"

  @bdd
  Scenario: Navigation
    Given app is opened
    Then menu is not empty
