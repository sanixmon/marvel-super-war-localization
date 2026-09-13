CXX = aarch64-linux-gnu-g++
CXXFLAGS = -std=c++17 -O3 -fPIC -Wall -Wextra -static-libstdc++
LDFLAGS = -shared -ldl

TARGET = liblocnative.so
SRCS = hook_main.cpp

all: $(TARGET)

$(TARGET): $(SRCS) dictionary_data.h
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
