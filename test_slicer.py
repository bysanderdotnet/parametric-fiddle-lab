import logging
from slice.slicer import slice_model

logging.basicConfig(level=logging.INFO)

try:
    slice_model('violin_body.step', 'dummy_profile', 'test_out.gcode')
except Exception as e:
    print(f"Test failed or errored expectedly: {e}")
