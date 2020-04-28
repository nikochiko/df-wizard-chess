=================================================
Dialogflow Fulfillment Server for Blindfold Chess
=================================================
Voice activated blindflod chess

Changelog
=========

v0.1.1
------
* Set up Travis CI
* Set up coverage reporting with Codecov
* Improve syntax

v0.1.0 - 27/04/2020
-------------------
* Format according to Black formatting tool
* Basic functionality to play a game as a Google Action
* Voice-activated ability to castle, promote pawn, and play move when at least the two squares involved in the move are given.
* Works with games stored in memory as `dict()` data type. Considering move to sqlite in future versions
* Unit tests added for most basic functions. More tests required for functions which handle intents.
* TODOs for next minor:
	* Add show_board intent to display the current board as an image.
	* Display board after game has ended
	* Store games in a database instead of dict()
	* Add support for simple SAN notation - intent, entity, intent-handler
	* Add support for when one piece and one square are mentioned - tell the user if move is ambiguous
	* Setup Travis CI with flake8 and coverage tools and cover at least 80% with unit tests
