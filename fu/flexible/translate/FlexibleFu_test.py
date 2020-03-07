"""
==========================================================================
FlexibleFu_test.py
==========================================================================
Test cases for flexible functional unit.

Author : Cheng Tan
  Date : Dec 14, 2019

"""

from pymtl3 import *
#from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL

from ..FlexibleFu                 import FlexibleFu
from ....lib.opt_type             import *
from ....lib.messages             import *

from ...single.Alu                import Alu
from ...single.Mul                import Mul
from ...single.Shifter            import Shifter
from ...single.Logic              import Logic
from ...single.Phi                import Phi
from ...single.MemUnit            import MemUnit
from ...single.Comp               import Comp
from ...single.Branch             import Branch

from pymtl3.passes.backends.verilog import TranslationImportPass

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, FuList, DataType, CtrlType, data_mem_size,
                 num_inports, num_outports, src0_msgs, src1_msgs,
                 ctrl_msgs, sink0_msgs, sink1_msgs ):

    s.src_in0   = TestSrcRTL( DataType, src0_msgs  )
    s.src_in1   = TestSrcRTL( DataType, src1_msgs  )
    s.src_const = TestSrcRTL( DataType, src1_msgs  )
    s.src_opt   = TestSrcRTL( CtrlType, ctrl_msgs  )
    s.sink_out0 = TestSinkRTL( DataType, sink0_msgs )
    s.sink_out1 = TestSinkRTL( DataType, sink1_msgs )

    s.dut = FunctionUnit( FuList, DataType, CtrlType, num_inports,
                          num_outports, data_mem_size )

    connect( s.src_const.send,  s.dut.recv_const )
    connect( s.src_in0.send,    s.dut.recv_in[0] )
    connect( s.src_in1.send,    s.dut.recv_in[1] )
    connect( s.src_opt.send,    s.dut.recv_opt   )
    connect( s.dut.send_out[0], s.sink_out0.recv )
    connect( s.dut.send_out[1], s.sink_out1.recv )

    is_memory_unit = False
    for i in range( s.dut.fu_list_size ):
      if hasattr(s.dut.fu[i], "to_mem_raddr"):
        is_memory_unit = True
    if is_memory_unit:
      s.dut.to_mem_raddr.rdy   //= 0
      s.dut.from_mem_rdata.en  //= 0
      s.dut.from_mem_rdata.msg //= DataType( 0, 0 )
      s.dut.to_mem_waddr.rdy   //= 0
      s.dut.to_mem_wdata.rdy   //= 0

  def done( s ):
    return s.src_in0.done()   and s.src_in1.done()   and\
           s.src_opt.done()   and s.sink_out0.done() and\
           s.sink_out1.done()

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=100 ):
  test_harness.elaborate()
  test_harness.dut.verilog_translate_import = True
  test_harness.dut.config_verilog_import = VerilatorImportConfigs(vl_Wno_list = ['UNSIGNED', 'UNOPTFLAT', 'WIDTH', 'WIDTHCONCAT', 'ALWCOMBORDER'])
  test_harness = TranslationImportPass()(test_harness)
  test_harness.apply( SimulationPass() )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

#def test_flexible_alu():
#  FU = FlexibleFu
#  FuList = [Alu]
#  DataType = mk_data( 16, 1 )
#  CtrlType = mk_ctrl()
#  data_mem_size = 8
#  num_inports   = 2
#  num_outports  = 2
#  src_in0  = [ DataType(1, 1), DataType(2, 1), DataType(9, 1) ]
#  src_in1  = [ DataType(2, 1), DataType(3, 1), DataType(1, 1) ]
#  sink_out = [ DataType(3, 1), DataType(5, 1), DataType(8, 1) ]
#  src_opt  = [ CtrlType(OPT_ADD), CtrlType(OPT_ADD), CtrlType(OPT_SUB) ]
#  th = TestHarness( FU, FuList, DataType, CtrlType, data_mem_size,
#                    num_inports, num_outports, src_in0, src_in1,
#                    src_opt, sink_out, sink_out )
#  run_sim( th )

def test_flexible_mul():
  FU = FlexibleFu
  FuList = [Alu, Mul]
  DataType = mk_data( 16, 1 )
  CtrlType = mk_ctrl()
  data_mem_size = 8
  num_inports   = 2
  num_outports  = 2
  src_in0  = [ DataType(1, 1), DataType(2, 1), DataType(9, 1) ]
  src_in1  = [ DataType(2, 1), DataType(3, 1), DataType(2, 1) ]
  sink_out = [ DataType(2, 1), DataType(6, 1), DataType(18, 1) ]
  src_opt  = [ CtrlType(OPT_MUL), CtrlType(OPT_MUL), CtrlType(OPT_MUL) ]
  th = TestHarness( FU, FuList, DataType, CtrlType, data_mem_size,
                    num_inports, num_outports, src_in0, src_in1,
                    src_opt, sink_out, sink_out )
  run_sim( th )

#def test_flexible_universal():
#  FU = FlexibleFu
#  FuList = [Alu, Mul, Logic, Shifter, Phi, Comp, Branch, MemUnit]
#  DataType = mk_data( 16, 1 )
#  CtrlType = mk_ctrl()
#  data_mem_size = 8
#  num_inports   = 2
#  num_outports  = 2
#  src_in0   = [ DataType(2, 1), DataType(2, 1), DataType(3, 0) ]
#  src_in1   = [ DataType(2, 1), DataType(0, 1), DataType(2, 1) ]
#  sink_out0 = [ DataType(1, 1), DataType(2, 1), DataType(2, 1) ]
#  sink_out1 = [ DataType(0, 0), DataType(2, 0), DataType(0, 0) ]
#  src_opt   = [ CtrlType(OPT_EQ), CtrlType(OPT_BRH), CtrlType(OPT_PHI) ]
#  th = TestHarness( FU, FuList, DataType, CtrlType, data_mem_size,
#                    num_inports, num_outports, src_in0, src_in1,
#                    src_opt, sink_out0, sink_out1 )
#  run_sim( th )
