// demo_layer.cc — Complete example showing how to add three-layer
// logging to a typical compute module (e.g., a neural network layer,
// a data processor, an algorithm kernel).
//
// This demonstrates the "Five Logging Points" pattern applied to 20+
// real modules in the caffe-ffi project.

#include "log.hpp"
#include <sstream>
#include <vector>

namespace myproj {

class DemoLayer {
 public:
  // ── Logging Point 1: Constructor / Initialization ─────
  explicit DemoLayer(int output_size, bool use_bias)
      : output_size_(output_size), use_bias_(use_bias) {
    // Log construction parameters
    MYPROJ_LAYER_LOG << "DemoLayer constructed: output_size=" << output_size_
                     << " use_bias=" << use_bias_;
  }

  // ── Logging Point 2: Setup / Configuration ────────────
  void Init(const std::vector<int64_t>& input_shape) {
    input_size_ = 1;
    for (auto d : input_shape) input_size_ *= d;

    // Log all parameters and derived values
    MYPROJ_LAYER_LOG << "DemoLayer Init: input_shape=" << ShapeToString(input_shape)
                     << " input_size=" << input_size_
                     << " output_size=" << output_size_;

    // Create internal buffers — log with TENSOR tag
    weight_buffer_.resize(input_size_ * output_size_, 0.0f);
    MYPROJ_TENSOR_LOG << "DemoLayer: created weight buffer ["
                      << input_size_ << "x" << output_size_ << "] = "
                      << weight_buffer_.size() << " floats";

    if (use_bias_) {
      bias_buffer_.resize(output_size_, 0.0f);
      MYPROJ_TENSOR_LOG << "DemoLayer: created bias buffer ["
                        << output_size_ << "] floats";
    }
  }

  // ── Logging Point 3: Reshape / Buffer Reallocation ────
  void Reshape(const std::vector<int64_t>& new_shape) {
    int new_size = 1;
    for (auto d : new_shape) new_size *= d;

    // Log before/after shape changes
    MYPROJ_LAYER_LOG << "DemoLayer Reshape: old_input_size=" << input_size_
                     << " new_input_size=" << new_size
                     << " new_shape=" << ShapeToString(new_shape);

    if (new_size != input_size_) {
      input_size_ = new_size;
      weight_buffer_.resize(input_size_ * output_size_, 0.0f);
      MYPROJ_TENSOR_LOG << "DemoLayer: resized weight buffer to ["
                        << input_size_ << "x" << output_size_ << "]";
    }
  }

  // ── Logging Point 4: Compute / Forward ────────────────
  float Forward(const float* input, float* output, int batch_size) {
    // Log compute dimensions ONCE before loops (NEVER inside loops!)
    MYPROJ_LAYER_LOG << "DemoLayer Forward: batch=" << batch_size
                     << " M=" << batch_size
                     << " N=" << output_size_
                     << " K=" << input_size_
                     << " use_bias=" << use_bias_;

    float total_loss = 0.0f;
    for (int b = 0; b < batch_size; ++b) {
      // ... actual computation ...
      for (int n = 0; n < output_size_; ++n) {
        float sum = use_bias_ ? bias_buffer_[n] : 0.0f;
        for (int k = 0; k < input_size_; ++k) {
          sum += input[b * input_size_ + k] * weight_buffer_[k * output_size_ + n];
        }
        output[b * output_size_ + n] = sum;
        total_loss += sum;
      }
    }

    // ── Logging Point 5: Result / Key Output Value ──────
    MYPROJ_LAYER_LOG << "DemoLayer Forward: total_loss=" << total_loss
                     << " (avg=" << total_loss / (batch_size * output_size_) << ")";
    return total_loss;
  }

 private:
  // Helper: format shape vector for logging
  static std::string ShapeToString(const std::vector<int64_t>& shape) {
    std::ostringstream ss;
    ss << "[";
    for (size_t i = 0; i < shape.size(); ++i) {
      if (i > 0) ss << ", ";
      ss << shape[i];
    }
    ss << "]";
    return ss.str();
  }

  int output_size_;
  bool use_bias_;
  int input_size_ = 0;
  std::vector<float> weight_buffer_;
  std::vector<float> bias_buffer_;
};

}  // namespace myproj
