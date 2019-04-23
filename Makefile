all: exolink

exolink: exolink.c
	gcc -O0 -g3 -o exolink exolink.c

clean:
	rm -rf *.o exolink

