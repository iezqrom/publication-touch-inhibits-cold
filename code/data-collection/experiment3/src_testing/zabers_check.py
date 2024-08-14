import sys
sys.path.append('..')
from local_functions import closeEnvelope, arduinos_zabers, triggeredException, arduinoSyringeControl, arduinoPantiltControl
from arduino import shakeShutter
from local_zaber_functions import manualControlPanTilt
import threading

if __name__ == "__main__":
    try:
        ### ARDUINOS & ZABERS
        (
            zabers, arduinos
        ) = arduinos_zabers()
        #### SHAKE SHUTTER
        shakeShutter(arduinos["syringe"], 5)

        # start thread for arduino syringe
        thread_syringe = threading.Thread(target = arduinoSyringeControl, args = [arduinos["syringe"]], daemon = True)
        thread_syringe.start()
        thread_pantilt = threading.Thread(target = arduinoPantiltControl, args = [arduinos["pantilt"]], daemon = True)
        thread_pantilt.start()

        ##### ZABER GAME
        manualControlPanTilt(zabers, home = False)

        #### HOMER ARDUINOS & ZABERS
        closeEnvelope(zabers, arduinos)

    except Exception as e:
        triggeredException(
            zabers=zabers,
            arduinos = arduinos,
            e=e,
        )

    except KeyboardInterrupt:
        triggeredException(
            zabers=zabers,
            arduinos = arduinos
        )
