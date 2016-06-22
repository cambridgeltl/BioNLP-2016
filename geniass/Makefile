CXX=g++
TARGET = geniass makeMapping remapStandOff
CFLAGS = -O2 -DNDEBUG
#CFLAGS = -g
geniass_OBJS = sample.o maxent.o blmvm.o
makeMapping_OBJS = makeMapping.o
remapStandOff_OBJS = remapStandOff.o

all: $(TARGET)

geniass: $(geniass_OBJS)
	$(CXX) $(CFLAGS) -o $@ $^

makeMapping: $(makeMapping_OBJS)
	$(CXX) $(CFLAGS) -o $@ $^

remapStandOff: $(remapStandOff_OBJS)
	$(CXX) $(CFLAGS) -o $@ $^

clean:
	/bin/rm -r -f $(OBJS) $(TARGET) *.o *~ model
.cpp.o:
	$(CXX) -c $(CFLAGS) $<
