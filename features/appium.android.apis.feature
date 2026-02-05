Feature: Appium.android.apis

  @bdd @smoke @mobile
  Scenario: Launch
    Given app is opened
    Then package should be "io.appium.android.apis"

  @bdd @mobile
  Scenario: Navigation
    Given app is opened
    Then menu is not empty
