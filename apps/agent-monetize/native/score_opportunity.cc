/*
 * agent-monetize native FFI module.
 * 使用 Apache TVM FFI（tvm-ffi）C++ API 注册 PackedFunc：
 *   - score_opportunity    机会打分（结构化计算）
 *   - risk_adjusted_net    风险调整净收益（结构化辅助计算）
 *
 * 编译方式（Windows）：见 build.ps1。加载本 DLL 后，静态初始化块会把上述
 * 函数注册进 tvm-ffi 全局注册表，Python 端经 `tvm_ffi.get_global_func`
 * 取回并调用。
 */
#include <tvm/ffi/tvm_ffi.h>

#include <algorithm>
#include <cmath>

namespace agent_monetize_native {

namespace ffi = tvm::ffi;

/*! \brief Clamp v into [lo, hi]. */
static double Clamp(double v, double lo, double hi) {
  return std::max(lo, std::min(hi, v));
}

/*!
 * \brief 结构化机会打分。
 *
 * 综合四类因子：
 *   base = max(0, 预期收益) * clamp(确定性, 0, 1) * (1 + clamp(稀缺因子, 0, 3))
 *   score = pow(base / (1 + max(0, 成本)), 0.8)，再 clamp 到 [0, 100]。
 *
 * 对应公理：A3（稀缺因子）、A2/A7（预期收益）、A4（成本惩罚）、A6（净收益）。
 */
static double ScoreOpportunity(double expected_return, double certainty,
                               double scarcity_factor, double est_cost) {
  double cert = Clamp(certainty, 0.0, 1.0);
  double scar = Clamp(scarcity_factor, 0.0, 3.0);
  double ret = std::max(0.0, expected_return);
  double cost = std::max(0.0, est_cost);
  double base = ret * cert * (1.0 + scar);
  double score = std::pow(base / (1.0 + cost), 0.8);
  return Clamp(score, 0.0, 100.0);
}

/*! \brief 风险调整净收益 = 预期收益 * 确定性 - 成本（结构化辅助计算）。 */
static double RiskAdjustedNet(double expected_return, double certainty,
                              double est_cost) {
  double cert = Clamp(certainty, 0.0, 1.0);
  return expected_return * cert - est_cost;
}

/*! \brief 静态初始化：注册全局 PackedFunc。 */
TVM_FFI_STATIC_INIT_BLOCK() {
  namespace refl = tvm::ffi::reflection;
  refl::GlobalDef()
      .def("score_opportunity", ScoreOpportunity)
      .def("risk_adjusted_net", RiskAdjustedNet);
}

}  // namespace agent_monetize_native
