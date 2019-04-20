all: exolink

exolink: exolink.c
	gcc -o exolink exolink.c

clean:
	rm -rf *.o exolink

