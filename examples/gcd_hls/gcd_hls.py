import siliconcompiler
import os


def main():
    root = os.path.dirname(__file__)
    chip = siliconcompiler.Chip('gcd')
    chip.input(os.path.join(root, "gcd.c"))
    chip.set('option', 'frontend', 'c')
    # default Bambu clock pin is 'clock'
    chip.clock(pin='clock', period=5)
    chip.load_target("freepdk45_demo")
    chip.run()
    chip.summary()
    chip.show()


if __name__ == '__main__':
    main()
