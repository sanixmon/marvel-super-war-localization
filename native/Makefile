NDK ?= /home/ubuntu/android-ndk
TOOLCHAIN = $(NDK)/toolchains/llvm/prebuilt/linux-x86_64
CXX = $(TOOLCHAIN)/bin/aarch64-linux-android21-clang++

CXXFLAGS = -std=c++17 -O3 -fPIC -Wall -Wextra -Wl,-z,max-page-size=16384
LDFLAGS = -shared -llog -Wl,-soname,liblocnative.so

TARGET = liblocnative.so
SRCS = hook_main.cpp

all: $(TARGET)

$(TARGET): $(SRCS) dictionary_data.h
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
