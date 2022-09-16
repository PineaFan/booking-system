1. [x] Incomplete
2. [x] Backend
3. [x] [Y] Frontend

### General Requirements:

- [ ] Easy to use system, with consistent fonts, colours and sizes. Users should be able to change the settings of the UI to match their needs.
- [X] Secure system; access is protected by usernames and passwords. All passwords must be at least 8 characters in length and must include upper case, and a digit.
- [X] There should be two layers of access rights; admin access right and general user access right.
- [X] Only Admin account holders can create new general accounts.
- [ ] All users should be able to change their passwords.


### Specific Requirements:

- [ ] All users including admin, should be able to create a new bookings, change and update existing bookings, and remove unwanted bookings.
- [ ] The system should archive any data older than 6 months.
- [X] All users must be able to change their passwords at any time.
- [X] Passwords must be hashed and slated before stored in database.
- [ ] The system should show welcome window to allow users to enter login details.
- [ ] The system should identify the user (admin or general user) from their username, and allow them the right menu; admin menu to admin users and general menu to general users.
- [ ] when an incorrect username/ passwords are entered, appropriate message should show that will help users to login correctly without revealing any details on the user name or passwords.
- [ ] After 3 unsuccessful attempts to login, the system should be locked for at least 1 hour.


### The general user menu should allow staff to:

- [ ] create a new bookings
- [ ] view an existing bookings
- [ ] Delete unwanted bookings


### Admin users should be able to have all the general menu functions as well as able to:

- [X] create a new general user accounts
- [X] change passwords for an existing accounts
- [X] delete an account.

- [ ] The system should reject double bookings, overbooking and any nonsense bookings.
- [ ] All data must be validated before accepted; no booking is allowed for more than 4 weeks in advance.
- [ ] the system should show graphs of number of bookings per day in yearly, monthly and weekly basis.
- [ ] Data base should be protected from injection.
- [ ] The system should be robust and will not crash if inappropriate data are used.
