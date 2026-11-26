# Source in Bash at build time or when opening a ROS terminal.
source /opt/ros/lyrical/setup.bash
_mpx_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Workspace root: WAFFLE_MPX_WS if set, else the parent of a ~/waffle_mpx/src clone,
# else the clone itself when colcon was run inside it (e.g. ~/waffle-mpx-lyrical).
if [[ -n "${WAFFLE_MPX_WS:-}" ]]; then
  _mpx_ws="$WAFFLE_MPX_WS"
elif [[ ! -f "$_mpx_repo/install/local_setup.bash" ]]; then
  _mpx_ws="$(dirname "$_mpx_repo")"
else
  _mpx_ws="$_mpx_repo"
fi
_mpx_root="$_mpx_ws/.cartographer"
if [[ -d "$_mpx_root/opt/ros/lyrical" ]]; then
  _mpx_arch="$(gcc -print-multiarch)"
  export CMAKE_PREFIX_PATH="$_mpx_root/opt/ros/lyrical:$_mpx_root/usr:${CMAKE_PREFIX_PATH:-}"
  export AMENT_PREFIX_PATH="$_mpx_root/opt/ros/lyrical:$AMENT_PREFIX_PATH"
  export LD_LIBRARY_PATH="$_mpx_root/opt/ros/lyrical/lib:$_mpx_root/usr/lib/$_mpx_arch:${LD_LIBRARY_PATH:-}"
  export CPATH="$_mpx_root/usr/include/$_mpx_arch${CPATH:+:$CPATH}"
fi
if [[ -f "$_mpx_ws/install/local_setup.bash" ]]; then
  source "$_mpx_ws/install/local_setup.bash"
else
  echo "lyrical_env: $_mpx_ws/install/local_setup.bash 가 없습니다. 워크스페이스에서 colcon build를 먼저 실행하세요. (저장소는 ~/waffle_mpx/src에 클론)" >&2
fi
unset _mpx_arch _mpx_root _mpx_repo _mpx_ws
