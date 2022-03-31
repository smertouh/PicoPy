#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PicoLog1000 series tango device server

"""

import time
import sys
import numpy
import json

import tango
from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt
from tango.server import Device, attribute, command, pipe, device_property

sys.path.append('../TangoUtils')
from TangoUtils import config_logger, restore_settings, save_settings, log_exception, Configuration, \
    LOG_FORMAT_STRING_SHORT
from TangoServerPrototype import TangoServerPrototype

from PicoLog1000 import *


def list_from_str(input_str):
    try:
        result = json.loads(input_str)
        if not isinstance(result, list):
            return []
        return result
    except:
        return []


class PicoPyServer(TangoServerPrototype):
    server_version = '2.0'
    server_name = 'PicoLog1000 series tango device server'
    device_list = []

    # scalar attributes
    picolog_type = attribute(label="type", dtype=str,
                             display_level=DispLevel.OPERATOR,
                             access=AttrWriteType.READ,
                             unit="", format="%s",
                             doc="Type of PicoLog1000 series device")

    info = attribute(label="info", dtype=str,
                     display_level=DispLevel.EXPERT,
                     access=AttrWriteType.READ,
                     unit="", format="%s",
                     doc="Info of PicoLog1000 series device")

    ping = attribute(label="ping_time", dtype=float,
                     display_level=DispLevel.OPERATOR,
                     access=AttrWriteType.READ,
                     unit="s", format="%f",
                     doc="Ping time")

    scale = attribute(label="scale", dtype=float,
                      display_level=DispLevel.OPERATOR,
                      access=AttrWriteType.READ,
                      unit="V", format="%f",
                      doc="Volts per ADC quantum")

    trigger = attribute(label="trigger", dtype=float,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="", format="%10.0f",
                        doc="Trigger index")

    overflow = attribute(label="overflow", dtype=int,
                         display_level=DispLevel.OPERATOR,
                         access=AttrWriteType.READ,
                         unit="", format="%d",
                         doc="Is there the overflow in recorded data")

    sampling = attribute(label="sampling", dtype=float,
                         display_level=DispLevel.OPERATOR,
                         access=AttrWriteType.READ,
                         unit="ms", format="%f",
                         doc="Sampling in milliseconds between points in each channel")

    record_in_progress = attribute(label="record_in_progress", dtype=bool,
                                   display_level=DispLevel.OPERATOR,
                                   access=AttrWriteType.READ_WRITE,
                                   unit="", format="",
                                   doc="Is record operation in progress")

    data_ready = attribute(label="data_ready", dtype=bool,
                           display_level=DispLevel.OPERATOR,
                           access=AttrWriteType.READ,
                           unit="", format="",
                           doc="Is data ready for reading")

    channel_record_time_us = attribute(label="channel_record_time_us", dtype=int,
                                       min_value=0,
                                       display_level=DispLevel.OPERATOR,
                                       access=AttrWriteType.READ_WRITE,
                                       unit="", format="%7d",
                                       doc="Channel record time in microseconds")

    points_per_channel = attribute(label="points_per_channel", dtype=int,
                                   min_value=0,
                                   max_value=1000000,
                                   display_level=DispLevel.OPERATOR,
                                   access=AttrWriteType.READ_WRITE,
                                   unit="", format="%7d",
                                   doc="Points per channel")

    channels = attribute(label="channels", dtype=str,
                         display_level=DispLevel.OPERATOR,
                         access=AttrWriteType.READ_WRITE,
                         unit="", format="%s",
                         doc='Channels list "[1, 2, 5]"')

    start_time = attribute(label="start_time", dtype=float,
                           display_level=DispLevel.OPERATOR,
                           access=AttrWriteType.READ,
                           unit="s", format="%f",
                           doc="Recording start time")

    stop_time = attribute(label="stop_time", dtype=float,
                          display_level=DispLevel.OPERATOR,
                          access=AttrWriteType.READ,
                          unit="s", format="%f",
                          doc="Recording stop time")
    # !!!!!!!!!!!!!!!!!!!!!
    # Channel numbering starts from 1 !!! (according manufacturer manuals and API)
    # !!!!!!!!!!!!!!!!!!!!!
    # channels for recorded ADC samples
    chany01 = attribute(label="Channel_01", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 01 data. 16 bit integers. Volts = data * display_units")

    chany02 = attribute(label="Channel_02", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 02 measurements. 16 bit integers, converted to Volts by display_units")

    chany03 = attribute(label="Channel_03", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 03 measurements. 16 bit integers, converted to Volts by display_units")

    chany04 = attribute(label="Channel_04", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 04 measurements. 16 bit integers, converted to Volts by display_units")

    chany05 = attribute(label="Channel_05", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 05 measurements. 16 bit integers, converted to Volts by display_units")

    chany06 = attribute(label="Channel_06", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 06 measurements. 16 bit integers, converted to Volts by display_units")

    chany07 = attribute(label="Channel_07", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 07 measurements. 16 bit integers, converted to Volts by display_units")

    chany08 = attribute(label="Channel_08", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 08 measurements. 16 bit integers, converted to Volts by display_units")

    chany09 = attribute(label="Channel_09", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 09 measurements. 16 bit integers, converted to Volts by display_units")

    chany10 = attribute(label="Channel_10", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 10 measurements. 16 bit integers, converted to Volts by display_units")

    chany11 = attribute(label="Channel_11", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 11 measurements. 16 bit integers, converted to Volts by display_units")

    chany12 = attribute(label="Channel_12", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 12 measurements. 16 bit integers, converted to Volts by display_units")

    chany13 = attribute(label="Channel_13", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 13 measurements. 16 bit integers, converted to Volts by display_units")

    chany14 = attribute(label="Channel_14", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 14 measurements. 16 bit integers, converted to Volts by display_units")

    chany15 = attribute(label="Channel_15", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 15 measurements. 16 bit integers, converted to Volts by display_units")

    chany16 = attribute(label="Channel_16", dtype=[numpy.uint16],
                        min_value=0,
                        max_value=4095,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="%5.3f",
                        doc="Channel 16 measurements. 16 bit integers, converted to Volts by display_units")

    # channels for ADC times 32 bit floats in ms
    chanx01 = attribute(label="Channel_01_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 01 counts. 32 bit floats in ms")
    chanx02 = attribute(label="Channel_02_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 02 counts. 32 bit floats in ms")
    chanx03 = attribute(label="Channel_03_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 03 counts. 32 bit floats in ms")
    chanx04 = attribute(label="Channel_04_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 04 counts. 32 bit floats in ms")
    chanx05 = attribute(label="Channel_05_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 05 counts. 32 bit floats in ms")
    chanx06 = attribute(label="Channel_06_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 06 counts. 32 bit floats in ms")
    chanx07 = attribute(label="Channel_07_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 07 counts. 32 bit floats in ms")
    chanx08 = attribute(label="Channel_08_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 08 counts. 32 bit floats in ms")
    chanx09 = attribute(label="Channel_09_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 09 counts. 32 bit floats in ms")
    chanx10 = attribute(label="Channel_10_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 10 counts. 32 bit floats in ms")
    chanx11 = attribute(label="Channel_11_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 11 counts. 32 bit floats in ms")
    chanx12 = attribute(label="Channel_12_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 12 counts. 32 bit floats in ms")
    chanx13 = attribute(label="Channel_13_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 13 counts. 32 bit floats in ms")
    chanx14 = attribute(label="Channel_14_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 14 counts. 32 bit floats in ms")
    chanx15 = attribute(label="Channel_15_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 15 counts. 32 bit floats in ms")
    chanx16 = attribute(label="Channel_16_times", dtype=[numpy.float32],
                        min_value=0.0,
                        max_dim_x=1000000,
                        max_dim_y=0,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="ms", format="%5.3f",
                        doc="Times for channel 16 counts. 32 bit floats in ms")
    # raw data for all channels
    raw_data = attribute(label="raw_data", dtype=[[numpy.uint16]],
                         max_dim_y=16,
                         max_dim_x=1000000,
                         min_value=0,
                         max_value=4095,
                         display_level=DispLevel.OPERATOR,
                         access=AttrWriteType.READ,
                         unit="V", format="%f",
                         doc="Raw data from ADC for all channels. 16 bit integers, converted to Volts by display_units")
    # timings for all  channels 32 bit floats in ms
    times = attribute(label="times", dtype=[[numpy.float32]],
                      max_dim_y=16,
                      max_dim_x=1000000,
                      min_value=0.0,
                      display_level=DispLevel.OPERATOR,
                      access=AttrWriteType.READ,
                      unit="ms", format="%f",
                      doc="ADC acquisition times for all channels. 32 bit floats in ms")

    def init_device(self):
        self.picolog = None
        self.device_type_str = "Unknown PicoLog device"
        self.device_name = ''
        self.channels_list = []
        self.record_initiated = False
        self.data_ready_value = False
        self.init_result = None
        self.points = 1000
        self.record_us = 1000000
        self.trigger_enabled = 0
        self.trigger_auto = 0
        self.trigger_auto_ms = 0
        self.trigger_channel = 1
        self.trigger_dir = 0
        self.trigger_threshold = 2048
        self.trigger_hysteresis = 100
        self.trigger_delay = 10.0
        # set logger and device proxy in super and then call self.set_config()
        super().init_device()
        if self not in PicoPyServer.devices:
            PicoPyServer.device_list.append(self)

    def set_config(self):
        super().set_config()
        try:
            self.set_state(DevState.INIT)
            self.device_name = self.get_name()
            # create PicoLog1000 device
            self.picolog = PicoLog1000()
            self.set_state(DevState.ON)
            # change PicoLog1000 logger to class logger
            self.picolog.logger = self.logger
            # open PicoLog1000 device
            self.picolog.open()
            self.set_state(DevState.OPEN)
            self.picolog.get_info()
            self.device_type_str = self.picolog.info['PICO_VARIANT_INFO']
            # set sampling interval channels and number of points
            self.set_sampling()
            # set properties for channels:
            self.configure_channels()
            # set trigger
            self.set_trigger()
            # OK message
            self.init_result = None
            msg = '%s %s has been initialized' % (self.device_name, self.device_type_str)
            self.logger.info(msg)
            self.set_state(DevState.STANDBY)
        except Exception as ex:
            self.init_result = ex
            log_exception('Exception initiating PicoLog %s', self.device_name)
            self.set_state(DevState.FAULT)

    def delete_device(self):
        try:
            self.picolog.stop()
        except:
            pass
        try:
            self.picolog.close()
        except:
            pass
        self.set_state(DevState.CLOSE)
        msg = '%s PicoLog has been deleted' % self.device_name
        self.logger.info(msg)
        self.info_stream(msg)

    def read_picolog_type(self):
        return self.device_type_str

    def read_info(self):
        return str(self.picolog.info)

    def read_ping(self):
        try:
            v = self.picolog.ping()
            return v
        except:
            msg = '%s Ping error %s' % (self.device_name, sys.exc_info()[1])
            self.logger.info(msg)
            self.info_stream(msg)
            self.logger.debug('', exc_info=True)
            return -1.0

    def read_scale(self):
        return self.picolog.scale

    def read_trigger(self):
        return self.picolog.trigger

    def read_overflow(self):
        return self.picolog.overflow

    def read_sampling(self):
        return self.picolog.sampling

    def read_record_in_progress(self):
        return self.record_initiated

    def write_record_in_progress(self, value: bool):
        if value:
            if self.record_initiated:
                return
            else:
                self.start_recording()
        else:
            if self.record_initiated:
                self.stop_recording()
            else:
                return

    def read_data_ready(self):
        return self.data_ready_value

    def read_channel_record_time_us(self):
        return self.picolog.record_us

    def write_channel_record_time_us(self, value):
        self.record_us = value
        self.set_device_property('channel_record_time_us', str(value))
        self.picolog.set_timing(self.channels_list, self.points, self.record_us)
        return self.picolog.record_us

    def read_points_per_channel(self):
        return self.points

    def write_points_per_channel(self, value):
        self.points = value
        self.set_device_property('points_per_channel', str(value))
        self.picolog.set_timing(self.channels_list, self.points, self.record_us)
        return self.points

    def read_channels(self):
        return str(self.channels_list)

    def write_channels(self, value):
        if isinstance(value, list):
            self.channels_list = value
        else:
            self.channels_list = list_from_str(value)
        self.set_device_property('channels', str(self.channels_list))
        self.picolog.set_timing(self.channels_list, self.points, self.record_us)

    def read_start_time(self):
        return self.picolog.run_time

    def read_stop_time(self):
        return self.picolog.read_time

    def name_from_number(self, n: int, xy='x'):
        return 'chan%s%02i' % (xy, n)

    def read_channel_data(self, channel: int, xy='y'):
        channel_name = self.name_from_number(channel, xy)
        if not hasattr(self, channel_name):
            msg = '%s Read for unknown channel %s' % (self.device_name, channel_name)
            self.logger.info(msg)
            return numpy.zeros(0, dtype=numpy.uint16)
        channel_attribute = getattr(self, channel_name)
        if channel not in self.channels_list:
            channel_attribute.set_quality(AttrQuality.ATTR_INVALID)
            msg = '%s Channel %s is not set for measurements' % (self.device_name, channel_name)
            self.logger.info(msg)
            self.error_stream(msg)
            return numpy.zeros(0, dtype=numpy.uint16)
        if not self.data_ready_value:
            channel_attribute.set_quality(AttrQuality.ATTR_INVALID)
            msg = '%s Data is not ready for %s' % (self.device_name, channel_name)
            self.logger.info(msg)
            self.error_stream(msg)
            return numpy.zeros(0, dtype=numpy.uint16)
        channel_index = self.channels_list.index(channel)
        self.logger.debug('%s Reading %s: %s', self.device_name, channel_name, self.picolog.data[0, :].shape)
        channel_attribute.set_quality(AttrQuality.ATTR_VALID)
        if xy == 'y':
            return self.picolog.data[channel_index, :]
        else:
            return self.picolog.times[channel_index, :]

    def read_chany01(self):
        return self.read_channel_data(1)

    def read_chany02(self):
        return self.read_channel_data(2)

    def read_chany03(self):
        return self.read_channel_data(3)

    def read_chany04(self):
        return self.read_channel_data(4)

    def read_chany05(self):
        return self.read_channel_data(5)

    def read_chany06(self):
        return self.read_channel_data(6)

    def read_chany07(self):
        return self.read_channel_data(7)

    def read_chany08(self):
        return self.read_channel_data(8)

    def read_chany09(self):
        return self.read_channel_data(9)

    def read_chany10(self):
        return self.read_channel_data(10)

    def read_chany11(self):
        return self.read_channel_data(11)

    def read_chany12(self):
        return self.read_channel_data(12)

    def read_chany13(self):
        return self.read_channel_data(13)

    def read_chany14(self):
        return self.read_channel_data(14)

    def read_chany15(self):
        return self.read_channel_data(15)

    def read_chany16(self):
        return self.read_channel_data(16)

    def read_chanx01(self):
        return self.read_channel_data(1, xy='x')

    def read_chanx02(self):
        return self.read_channel_data(2, xy='x')

    def read_chanx03(self):
        return self.read_channel_data(3, xy='x')

    def read_chanx04(self):
        return self.read_channel_data(4, xy='x')

    def read_chanx05(self):
        return self.read_channel_data(5, xy='x')

    def read_chanx06(self):
        return self.read_channel_data(6, xy='x')

    def read_chanx07(self):
        return self.read_channel_data(7, xy='x')

    def read_chanx08(self):
        return self.read_channel_data(8, xy='x')

    def read_chanx09(self):
        return self.read_channel_data(9, xy='x')

    def read_chanx10(self):
        return self.read_channel_data(10, xy='x')

    def read_chanx11(self):
        return self.read_channel_data(11, xy='x')

    def read_chanx12(self):
        return self.read_channel_data(12, xy='x')

    def read_chanx13(self):
        return self.read_channel_data(13, xy='x')

    def read_chanx14(self):
        return self.read_channel_data(14, xy='x')

    def read_chanx15(self):
        return self.read_channel_data(15, xy='x')

    def read_chanx16(self):
        return self.read_channel_data(16, xy='x')

    def read_raw_data(self):
        if self.data_ready_value:
            self.logger.debug('%s Reading raw_data %s', self.device_name, self.picolog.data.shape)
            self.raw_data.set_quality(AttrQuality.ATTR_VALID)
            return self.picolog.data
        else:
            self.raw_data.set_quality(AttrQuality.ATTR_INVALID)
            msg = '%s Data is not ready' % self.device_name
            self.logger.warning(msg)
            self.error_stream(msg)
            return numpy.zeros(0, dtype=numpy.uint16)

    def read_times(self):
        if self.data_ready_value:
            self.logger.debug('%s Reading times %s', self.device_name, self.picolog.times.shape)
            self.times.set_quality(AttrQuality.ATTR_VALID)
            return self.picolog.times
        else:
            self.times.set_quality(AttrQuality.ATTR_INVALID)
            msg = '%s Data is not ready' % self.device_name
            self.logger.warning(msg)
            self.error_stream(msg)
            return numpy.zeros(0, dtype=numpy.uint16)

    @command(dtype_in=str, dtype_out=str)
    def _read_picolog_attribute(self, name):
        if hasattr(self.picolog, name):
            return str(getattr(self.picolog, name))
        else:
            return 'Attribute not found'

    @command(dtype_in=int)
    def _start(self, value):
        try:
            if value > 0:
                if self.record_initiated:
                    msg = '%s Can not start - record in progress' % self.device_name
                    self.logger.info(msg)
                    self.info_stream(msg)
                    return
            if value > 1:
                if not self.picolog.ready():
                    msg = '%s Can not start - device not ready' % self.device_name
                    self.logger.info(msg)
                    self.info_stream(msg)
                    return
            self.picolog.run()
            self.start_time_value = time.time()
            self.record_initiated = True
            self.data_ready_value = False
            self.set_state(DevState.RUNNING)
            msg = '%s Recording started' % self.device_name
            self.logger.info(msg)
            self.info_stream(msg)
        except:
            self.record_initiated = False
            self.data_ready_value = False
            self.set_state(DevState.FAULT)
            msg = '%s Recording start error' % self.device_name
            self.logger.warning(msg)
            self.error_stream(msg)
            self.logger.debug('', exc_info=True)

    @command(dtype_in=None)
    def start_recording(self):
        self.stop_recording()
        self._read_config()
        self._start(0)

    @command(dtype_in=None)
    def _read_config(self):
        self.stop_recording()
        self.set_sampling()
        # set trigger
        self.set_trigger()
        self.record_initiated = False
        self.data_ready_value = False
        self.set_state(DevState.STANDBY)
        msg = '%s New config applied' % self.device_name
        self.logger.debug(msg)
        self.debug_stream(msg)

    @command(dtype_in=None)
    def stop_recording(self):
        try:
            self.picolog.stop()
            self.record_initiated = False
            self.data_ready_value = False
            self.set_state(DevState.STANDBY)
            msg = '%s Recording stopped' % self.device_name
            self.logger.info(msg)
            self.info_stream(msg)
        except:
            self.record_initiated = False
            self.data_ready_value = False
            self.set_state(DevState.FAULT)
            msg = '%s Recording stop error' % self.device_name
            self.logger.warning(msg)
            self.error_stream(msg)
            self.logger.debug('', exc_info=True)

    def assert_proxy(self):
        if not hasattr(self, 'device_proxy') or self.device_proxy is None:
            self.device_proxy = tango.DeviceProxy(self.device_name)

    def set_channel_properties(self, chan, props=None):
        try:
            if not isinstance(chan, attribute):
                chan = getattr(self, str(chan))
            if props is None:
                props = {}
            prop = chan.get_properties()
            prop.display_unit = self.picolog.scale
            prop.max_value = self.picolog.max_adc
            try:
                for p in props:
                    if hasattr(prop, p):
                        setattr(prop, p, props[p])
            except:
                pass
            chan.set_properties(prop)
        except:
            log_exception('Properties set error')

    def configure_channels(self):
        for i in range(1, 16):
            self.set_channel_properties(self.name_from_number(i))
            self.set_channel_properties(self.name_from_number(i, xy='x'),
                                        {'display_unit': 1.0,
                                         'max_value': self.picolog.times[0, :].max()})
        self.set_channel_properties(self.raw_data)
        self.self.raw_data.set_value(self.picolog.data)

    def set_sampling(self):
        # read input channels list
        value = self.config.get('channels', '[1]')
        self.channels_list = list_from_str(value)
        # read sampling interval and number of points
        self.points = self.config.get('points_per_channel', 1000)
        self.record_us = self.config.get('channel_record_time_us', 1000000)
        # set sampling interval and number of points
        self.picolog.set_timing(self.channels_list, self.points, self.record_us)

    def set_trigger(self):
        # raed trigger parameters
        self.trigger_enabled = self.self.config.get('trigger_enabled', 0)
        self.trigger_auto = self.self.config.get('trigger_auto', 0)
        self.trigger_auto_ms = self.self.config.get('trigger_auto_ms', 0)
        self.trigger_channel = self.self.config.get('trigger_channel', 1)
        self.trigger_dir = self.self.config.get('trigger_direction', 0)
        self.trigger_threshold = self.self.config.get('trigger_threshold', 2048)
        self.trigger_hysteresis = self.self.config.get('trigger_hysteresis', 100)
        self.trigger_delay = self.self.config.get('trigger_delay', 10.0)
        # set trigger
        self.picolog.set_trigger(self.trigger_enabled, self.trigger_channel,
                                 self.trigger_dir, self.trigger_threshold,
                                 self.trigger_hysteresis, self.trigger_delay,
                                 self.trigger_auto, self.trigger_auto_ms)


def looping():
    time.sleep(0.001)
    for dev in PicoPyServer.device_list:
        if dev.record_initiated:
            try:
                if dev.picolog.ready():
                    dev.stop_time_value = time.time()
                    dev.picolog.read()
                    dev.record_initiated = False
                    dev.data_ready_value = True
                    msg = '%s Recording finished, data is ready' % dev.device_name
                    dev.logger.info(msg)
                    dev.info_stream(msg)
            except:
                dev.record_initiated = False
                dev.data_ready_value = False
                msg = '%s Reading data error' % dev.device_name
                dev.logger.warning(msg)
                dev.error_stream(msg)
                dev.logger.debug('', exc_info=True)
    # PicoPyServer.logger.debug('loop end')


if __name__ == "__main__":
    PicoPyServer.run_server(event_loop=looping)
