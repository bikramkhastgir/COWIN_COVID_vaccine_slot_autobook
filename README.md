# Co-Win Portal Vaccination Slot Auto-Booking Script
A Python package to facilitate the notification and auto booking of vaccine slots through the Co-WIN Public APIs. This script checks available slots in vaccination centers at the areas of interest (by district or pincode) and notifies users as soon as slots become avalibale (using a beep sound, winsound package) and tries to book the slots for the selected beneficiaries.  



The OTP will be needed to be entred manually. This is a simplified version from Bombardier's package which requires some more setting up to automate the capture of OTP from mobile.
Also once a slot if available, the CAPTCHA will pop-up and the user needs to manually enter it.



Note: 
  1) I have created this to facilitate booking of COVID vaccines throught the publicly available APIs. I do not gain any monetary benifits through the use of this package nor for endorsing others to use this. 
  2) This is a personal project and has been uploaded to benifit those who are unable to get notification or are unavailable to book from the Co-WIN portal as vaccination slots become available. 
  3) The API calls have a sleep time to enable the program to send around 100 calls every 5 mins. (https://apisetu.gov.in/public/api/cowin)
  4) The material embodied in this package is provided to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty for a particular purpose.
  5) This is highly refrenced from 'https://github.com/bombardier-gif/covid-vaccine-booking' . Special thanks to 'https://github.com/pallupz' for building a base for this code. 
  
Python libraries used (mainly to help pop-up the CAPTCHA):
> svglib

> PySimpleGUI

> Pillow
