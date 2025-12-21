import numba


@numba.jit(
    numba.void(
        numba.int32[:, :, ::1],
        numba.float32[:, :, ::1],
        numba.int32[::1],
        numba.int32[::1],
    ),
    nopython=True,
    nogil=True,
)
def maximum_path_jit(paths, values, t_ys, t_xs):
    b = paths.shape[0]
    max_neg_val = -1e9
    for i in range(int(b)):
        path = paths[i]
        value = values[i]
        t_y = t_ys[i]
        t_x = t_xs[i]
        
        # 수정: t_y나 t_x가 0 이하인 경우 처리 (빈 범위 방지)
        if t_y <= 0 or t_x <= 0:
            continue

        v_prev = v_cur = 0.0
        index = t_x - 1

        for y in range(t_y):
            for x in range(max(0, t_x + y - t_y), min(t_x, y + 1)):
                if x == y:
                    v_cur = max_neg_val
                else:
                    v_cur = value[y - 1, x]
                if x == 0:
                    if y == 0:
                        v_prev = 0.0
                    else:
                        v_prev = max_neg_val
                else:
                    v_prev = value[y - 1, x - 1]
                value[y, x] += max(v_prev, v_cur)

        # 수정: t_y가 1 이상인 경우에만 역순 루프 실행
        if t_y > 0:
            for y in range(t_y - 1, -1, -1):
                path[y, index] = 1
                if index != 0 and (
                    index == y or value[y - 1, index] < value[y - 1, index - 1]
                ):
                    index = index - 1
