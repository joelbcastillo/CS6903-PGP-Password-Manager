CS6903 Project 2 - COVID-19 Vaccine Passport Checker
===================================================

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

* Github Repository:  <https://github.com/joelbcastillo/CS6903-Vaccine-Passport-Checker.git>

Description
-----------

The COVID19 Vaccine Passport Checker is an open-source web application that allows patrons of an establishment, such as a library, coffee shop, or coworking space, to fill out a reservation and include PHI information such as their Excelsior Pass QR code or PCR test results securely. The application can securely analyze this data and determine whether a patron can enter the establishment without actually exposing the PHI of the patron to employees at the establishment.

The front-end will utilize a Javascript PGP library ([KBPGP.js](https://keybase.io/kbpgp)) to allow the user to create and store their own PGP key pair or import an existing key pair for use with the application. The form will be filled out by the user after providing their credentials. Fields that contain PHI will be encrypted using homomorphic encryption and stored in the database. The submission will be signed by the users PGP key to attest to it's validity. A separate confirmation with QR code and confirmation number will be generated and provided to the user so that they can check in upon arrival to the establishment.

Upon arrival, an employee of the establishment can scan the QR code or lookup the confirmation number to verify whether the patron can enter the venue. To validate the patron's identity, we plan on using Keybase to validate the owner of the PGP key used to sign the reservation is owned by the patron who provided the QR code / confirmation number at the door to the establishment.

Authors
-------

* Ho Yin Kenneth Chan ([@kenliya](https://github.com/kenliya))
* Gary Zhou ([@g-zhou](https://github.com/g-zhou))
* Joel Castillo ([@joelbcastillo](https://github.com/joelbcastillo))
