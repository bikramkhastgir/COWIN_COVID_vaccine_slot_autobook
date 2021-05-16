# Co-Win Portal Vaccination Slot Auto-Booking Script
A Python package to facilitate the notification and auto booking of vaccine slots through the Co-WIN Public APIs. This script checks available slots in vaccination centres at the areas of interest (by district or pincode) and notifies users as soon as slots become available (using a beep sound, winsound package) and try to book the slots for the selected beneficiaries.

- The OTP will be needed to be entered manually. This is a simplified version from Bombardier's package which requires some more setting up to automate the capture of OTP from mobile. 
- Also once a slot is available, the CAPTCHA will pop up and the user needs to manually enter it.
- Once the slots are booked, it will be reflected in the Co-WIN portal (https://www.cowin.gov.in/) by logging in through the same mobile number entered in this script for OTP.
- Search enabled with district only for now. ** 


Note:
  1) I have created this to facilitate the booking of COVID vaccines through the publicly available APIs. I do not gain any monetary benefits through the use of this package nor for endorsing others to use this.
  2) This is a personal project and has been uploaded to benefit those who are unable to get a notification or are unavailable to book from the Co-WIN portal as vaccination slots become available. These scripts in itself are not backed by any organization or by the Government of India. 
  3) The API calls have a sleep time to enable the program to send around 100 calls every 5 mins. (https://apisetu.gov.in/public/api/cowin)
  4) The material embodied in this package is provided to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty for a particular purpose.
  5) This is highly referenced from 'https://github.com/bombardier-gif/covid-vaccine-booking'. Special thanks to 'https://github.com/pallupz' for building a base for this code.
  6) Some parameters like first dose and no vaccine preferences are hard coded in this script, please check carefully before booking. These will be made user interactable in the coming updates. 

To Run:
  1) Use command prompt, goto the location where these files are downloaded.
  2) Type 'python cowin_script.py'.
  3) Enter details as prompted.
  4) To reset mobile number or location preference, simply goto the 'registered_mobile_number.txt' or 'location_details.txt' that will be generated after the first run and remove the saved details.

Python libraries used (mainly to help pop-up the CAPTCHA):
> svglib

> PySimpleGUI

> Pillow
