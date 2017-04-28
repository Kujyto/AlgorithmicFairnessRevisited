#!/bin/bash

E_BADARGS=85

if [ ! -n "$1" ]
then
  echo "Usage: `basename $0` nbSamples"
  exit $E_BADARGS
fi

OUTPUT="../data/contre_exemple.data"

COUNT=$1
echo "$COUNT samples for each race"

FRAC_BLACK=50
FRAC_WHITE=80
FRAC_HISP=20

# empty file
echo "" > $OUTPUT

function generate {
    RACE=$1
    FRAC=$2

    for i in $(seq 1 $COUNT)
    do
        X=$RANDOM
        Y=$RANDOM
        let "X %= 2"
        let "Y %= 2"
        hire=$RANDOM
        let "hire %= 100"
        if [ "$hire" -lt "$FRAC" ]; then
            echo "$RACE, $X, $Y, Yes" >> $OUTPUT
        else
            echo "$RACE, $X, $Y, No" >> $OUTPUT
        fi
    done
}


generate "Black" $FRAC_BLACK
generate "White" $FRAC_WHITE
generate "Hispanic" $FRAC_HISP


exit 0
