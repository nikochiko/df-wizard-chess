==========================
Wizard Chess w/ Dialogflow
==========================
.. image:: https://travis-ci.com/nikochiko/chess-server.svg?token=Tv6EyBGSze8NLsac3zQC&branch=master
    :target: https://travis-ci.com/nikochiko/chess-server
.. image:: https://codecov.io/gh/nikochiko/chess-server/branch/master/graph/badge.svg?token=HMjzAbiZU1
    :target: https://codecov.io/gh/nikochiko/chess-server
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

🤔 What is this?
================
To truly understand what Wizard Chess is, I will have you read this

    **What do you do when you really want to play blindfold chess but you're stuck at home? 🏠**
    
    *Ask your chess friends - easy 👨‍👨‍👧‍👦*
    
    **They don't like blindfold 🤷**
    
    *Google for an online solution 💻, there are so many chess apps. There has to be one about blindfold chess.*
    
    **Pbbt 👅 There ain't one.**
    
    *What about.. the popular ones?*
    
    **They say "hide your pieces, it's just like blindfold chess 😇"**
    
    *Ugh - that's a scam*
    
    **I have to do something about this.. 👨‍🔧🍳**
    
That right there - was the birth of this project. Wizard Chess is in the spirit (if not *the spirit* 👻) of
blindfold chess. Keeping that in mind, the vision is to support playing *real* blindfold chess the best way, while
also being just as pleasant to the learner and the amateur 😄.

🧐 How do you do it?
====================
	When the spirit 👻 of blindfold chess interacts with the wizardry 🔮 of AI assistants,
	
	> **the matrix has you** 😎

⏰ Changelog
============

v0.1.1
------
* Set up Travis CI
* Set up coverage reporting with Codecov
* Moved from using Dict in memory to sqlite3 DB on disk 🎉
* Added testing to cover more than 90% of codebase 💪
* Added feature to see board at any time 👁️
* Board image will be shown after completion of games 📜


v0.1.0 - 27/04/2020
-------------------
* Format according to Black formatting tool
* Basic functionality to play a game as a Google Action
* Voice-activated ability to castle, promote pawn, and play move when at least the two squares involved in the move are given.
* Works with games stored in memory as `Dict` data type. Considering move to sqlite in future versions
* Unit tests added for most basic functions. More tests required for functions which handle intents.
* TODOs for next minor:
	* Add show_board intent to display the current board as an image.
	* Display board after game has ended
	* Store games in a database instead of Dict
	* Add support for simple SAN notation - intent, entity, intent-handler
	* Add support for when one piece and one square are mentioned - tell the user if move is ambiguous
	* Setup Travis CI with flake8 and coverage tools and cover at least 80% with unit tests
