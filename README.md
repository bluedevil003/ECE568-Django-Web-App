# erss-hwk1-kx30-kw300

This is the repository of our ECE568 first homework.

## Page Introduction ##

* /                   --- Default login page
* /signup             --- signup page
* /homepage           --- homepage, list all available ride
* /ride/\<int:ride_id\> --- detail info of one ride
* /user/\<int:user_id\> --- detail info of the user

##  Notes ##

1. how to migrate

Because we config postgres in docker, anything you want to interact with the DB, you need `sudo docker-compose run web` before(this will ensure you run in docker environment). e.g. you want to enter shell and interact with DB

run
```shell
sudo docker-compose run web python3 managers.py shell
```

instead simply run

```shell
python3 managers.py shell
```

2. how to prettfy your html code

* `C-x h` --- select the whole buffer
* `M-x indent-region`(`C-M-\`)

Package we need:
passlib (1.7.2)
