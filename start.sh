#!/usr/bin/env sh

# Are you using docker-compose challenge containers? Set to 1.
CHALLENGE_COMPOSE=0

# Help
help(){
USAGE="Usage: $0 [OPTION]
Run CTFd with preconfigured setup.yml

Options:
  -s, --start     Start CTFd with preconfigured setup.yml,
                      also starts docker challenges
  -c, --clean     Clean CTFd from any configurations made
  -h, --help      display this help text and exit


Read README.md and docs if in doupt.
Remember to configure setup.yml.
Set 'CHALLENGE_COMPOSE=1' if 'docker-compose up' for challenges is wanted.
" 

printf "%s" "$USAGE"
exit 0
}


# Delete 
clean(){
cd CTFd
[ -d .data ] && echo "Removing .data" && rm -rf .data 
git reset --hard origin
git clean -df
}


# Timezone annoyance, needed for accurate timesetup in CTFd
tz(){
tail -n 1 /etc/localtime |\
    sed -En 's/\w*([-+]?[0-9]*:?[0-9]*)\w*.*/\1/p' \
    > OCD/config_files/tz
}


# Start
start(){
echo "Checking setup.yml syntax"
python3 OCD/CTFd_setup/check_yaml.py OCD/setup.yml || exit 1

echo "Copying files into CTFd"
cp -r OCD CTFd

# In CTFd directory
cd CTFd

# Setup for entry
tz
mv OCD/CTFd_setup/OCD.py .
mv OCD/CTFd_setup/db.py .

# Needed for YAML in docker
echo "PyYAML==3.13" >> requirements.txt

# Needed for docker CTFd to call OCD.py
INSERTENTRY='# Create the database\necho "Creating database"\npython OCD.py || echo "Skipping database creation"\n\n# Start CTFd'
sed -i "s/^# Start CTFd$/$INSERTENTRY/" docker-entrypoint.sh

# Needed for MariaDB versioning bug
MARIA='    image: mariadb:10.4.12'
sed -i "s/^    image: mariadb:10.4$/$MARIA/" docker-compose.yml


# Start
echo "Starting CTFd"
docker-compose up -d > /dev/null

# Wait for website to be running
echo "Waiting for CTFd to be running"
while ! curl -sL localhost:8000 > /dev/null
do
    echo -n '.'
    sleep 1
done

# Restart cache on setup, skip if already setup
WSITE=$(curl -sL localhost:8000)

case "$WSITE"
in 
    *id=\"setup-form\"*) echo '\nSkipping setup' ; 
                         docker-compose rm -sf cache ; 
                         rm -rf .data/redis ;
                         docker-compose up -d cache > /dev/null ;;
    *) echo '\nSetup already done' ;;
esac

echo "CTFd setup done"
}


dockerchallenges(){
cd ..

# In CTFdeploy
[ $CHALLENGE_COMPOSE -eq 0 ] && exit 0
[ ! -f OCD/docker_challenges/docker-compose.yml ] || echo 'No docker-compose.yml found in OCD/docker_challenges. Exiting.' && exit 1
cd OCD/docker_challenges

echo 'Starting challenge containers'
docker-compose up -d

echo 'Docker challenge containers done'
}


# Case for intentions
case $1 in
    -s|--start) start; dockerchallenges;;
    -c|--clean) clean ;;
    -h|--help|*) help ;;
esac
