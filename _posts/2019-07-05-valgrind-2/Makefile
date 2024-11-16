SUFFICES = 
SUFFICES = .f90

SRCS = mytypes.f90 main.f90
OBJS = $(patsubst %.f90, %.o, $(SRCS))

FCFLAGS = -O0 -g

FC = ifort

all: $(OBJS)
	$(FC) -o test $(OBJS) $(FCFLAGS) $(LDFLAGS)

%.o: %.f90
	$(FC) $(FCFLAGS) -c $<

clean:
	rm -f *.o *.mod test
