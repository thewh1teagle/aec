#[cfg(target_arch = "wasm32")]
use wasm_bindgen::prelude::*;

use std::os::raw::c_void;
/// See https://www.speex.org/docs/api/speex-api-reference/speex__echo_8h.html

#[derive(Debug, Clone)]
#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
pub struct AecConfig {
    pub frame_size: usize,
    pub filter_length: i32,
    pub sample_rate: u32,
    pub enable_preprocess: bool,
}

impl Default for AecConfig {
    /// Default for 16khz
    fn default() -> Self {
        Self {
            frame_size: 160,
            filter_length: 1600,
            sample_rate: 16000,
            enable_preprocess: true,
        }
    }
}

#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
pub struct Aec {
    echo_state: *mut aec_rs_sys::SpeexEchoState,
    preprocess_state: Option<*mut aec_rs_sys::SpeexPreprocessState>,
}

#[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
impl Aec {
    #[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
    pub fn new(config: &AecConfig) -> Self {
        let echo_state = unsafe {
            aec_rs_sys::speex_echo_state_init(config.frame_size as i32, config.filter_length)
        };
        let preprocess_state = if config.enable_preprocess {
            unsafe {
                let den = aec_rs_sys::speex_preprocess_state_init(
                    config.frame_size as i32,
                    config.sample_rate as _,
                );
                aec_rs_sys::speex_preprocess_ctl(
                    den,
                    aec_rs_sys::SPEEX_PREPROCESS_SET_ECHO_STATE as _,
                    echo_state as *mut c_void,
                );
                Some(den)
            }
        } else {
            None
        };

        Aec {
            echo_state,
            preprocess_state,
        }
    }

    #[cfg_attr(target_arch = "wasm32", wasm_bindgen)]
    pub fn cancel_echo(&self, rec_buffer: &[i16], echo_buffer: &[i16], out_buffer: &mut [i16]) {
        unsafe {
            aec_rs_sys::speex_echo_cancellation(
                self.echo_state,
                rec_buffer.as_ptr(),
                echo_buffer.as_ptr(),
                out_buffer.as_mut_ptr(),
            );
            if let Some(preprocess_state) = self.preprocess_state {
                aec_rs_sys::speex_preprocess_run(preprocess_state, out_buffer.as_mut_ptr());
            }
        }
    }
}

impl Drop for Aec {
    fn drop(&mut self) {
        unsafe {
            aec_rs_sys::speex_echo_state_destroy(self.echo_state);
            if let Some(preprocess_state) = self.preprocess_state {
                aec_rs_sys::speex_preprocess_state_destroy(preprocess_state);
            }
        }
    }
}
