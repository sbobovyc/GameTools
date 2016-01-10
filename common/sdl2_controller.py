import sys
import sdl2
import sdl2.ext

def run():
    sdl2.ext.init()
    sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
    window = sdl2.ext.Window("Controller test", size=(640,480))
    window.show()
    running = True

    if sdl2.joystick.SDL_NumJoysticks() < 1:
        print "No joysticks plugged in"
        return 0

    joystick = sdl2.SDL_JoystickOpen(0)
    print "Name:",      sdl2.SDL_JoystickName(joystick)
    print "NumAxes",        sdl2.SDL_JoystickNumAxes(joystick)
    print "Trackballs:",    sdl2.SDL_JoystickNumBalls(joystick)
    print "Buttons:",       sdl2.SDL_JoystickNumButtons(joystick)
    print "Hats:",          sdl2.SDL_JoystickNumHats(joystick)
    print "Haptic?:",          sdl2.SDL_JoystickIsHaptic(joystick)

    #sdl2.SDL_JoystickClose(joystick)
    #return 0

    while(running):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_JOYAXISMOTION:
                print "======================="
                for axis in range(sdl2.SDL_JoystickNumAxes(joystick)):
                    print "Axis: %i, value: %i" % (axis, sdl2.SDL_JoystickGetAxis(joystick, axis))
            if event.type == sdl2.SDL_JOYBUTTONDOWN:
                print "======================="
                for button in range(sdl2.SDL_JoystickNumButtons(joystick)):
                    print "Button: %i, value: %i" % (button, sdl2.SDL_JoystickGetButton(joystick, button))
            if event.type == sdl2.SDL_JOYHATMOTION:
                print "======================="
                for hat in range(sdl2.SDL_JoystickNumHats(joystick)):
                    print "Hat: %i, value: %i" % (hat, sdl2.SDL_JoystickGetHat(joystick, hat))
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        window.refresh()
    return 0

if __name__ == "__main__":
    sys.exit(run())
