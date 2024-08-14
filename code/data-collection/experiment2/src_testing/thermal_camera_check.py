import sys
sys.path.append('..')
#### OWN LIBRARIES
from camera import TherCam, changeValuesColorBar
from zabers import movetostartZabersConcu

#### EXTERNAL LIBRARIES
from grabPorts import grabPorts
from globals import centre_grid_positions, haxes, position_z_camera_check, data_path, vmin_file_name, vmax_file_name
from local_functions import closeEnvelope, arduinos_zabers, triggeredException, writeNumber, checkVminVmax

if __name__ == "__main__":
    try:
        ports = grabPorts()
        print(ports.ports)

        ## ARDUINOS & ZABERS
        (
            zabers,
            arduinos
        ) = arduinos_zabers()

        #### CAMERA TO POSITION TO CHECK IT
        centre_grid_positions["camera"]["z"] = position_z_camera_check
        movetostartZabersConcu(
            zabers, "camera", haxes["colther"], pos = centre_grid_positions["camera"]
        )

        #### START THERMAL CAMERA
        vminT, vmaxT = checkVminVmax(data_path, vmin_file_name, vmax_file_name)
        cam = TherCam(vminT, vmaxT)

        changeValuesColorBar(cam)

        cam.startStream()
        cam.plotLive()

        writeNumber(cam.vminT, data_path, vmin_file_name)
        writeNumber(cam.vmaxT, data_path, vmax_file_name)

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
            arduinos = arduinos,
        )
