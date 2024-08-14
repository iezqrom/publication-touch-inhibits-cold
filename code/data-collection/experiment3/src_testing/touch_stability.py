import sys
sys.path.append('..')
from grabPorts import grabPorts
from local_functions import closeEnvelope, arduinos_zabers, triggeredException

from zabers import movetostartZabersConcu

from globals import stability

if __name__ == "__main__":
    try:
        ports = grabPorts()
        print(ports.ports)

        ### ARDUINOS & ZABERS
        (
            zabers,
            arduinos
        ) = arduinos_zabers()

        input("Press enter to check next point")
        movetostartZabersConcu(
            zabers,
            "tactile",
            ["x", "y"],
            pos={
                "x": stability[0]["x"],
                "y": stability[0]["y"],
            },
        )

        movetostartZabersConcu(
            zabers,
            "tactile",
            ["z"],
            pos={
                "z": stability[0]["z"],
            },
        )

        input("Press enter to check next point")
        movetostartZabersConcu(
            zabers,
            "tactile",
            ["z"],
            pos={
                "z": 0,
            },
        )
        movetostartZabersConcu(
            zabers,
            "tactile",
            ["x", "y"],
            pos={
                "x": stability[1]["x"],
                "y": stability[1]["y"],
            },
        )
        movetostartZabersConcu(
            zabers,
            "tactile",
            ["z"],
            pos={
                "z": stability[1]["z"],
            },
        )

        input("Press enter to finish next point")
        #### HOMER ARDUINOS & ZABERS
        closeEnvelope(
            zabers, arduinos
        )

    except Exception as e:
        triggeredException(
            zabers=zabers,
            arduinos = arduinos,
            e=e,
        )

    except KeyboardInterrupt:
        triggeredException(
            zabers=zabers,
            arduinos = arduinos,
        )
