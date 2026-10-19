import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.colors import LogNorm

import imageio_ffmpeg
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
velocity = 1     #m/day
dt =3          #timestep in days

alphaL = 1      #Longitudinal dispersivity (m)
alphaT = .5      #Traversal dispersivity (m)

sigmaL = (2 * alphaL * velocity * dt  ) ** 0.5 #standard deviation of distribution 
sigmaT = (2 * alphaT * velocity * dt  ) ** 0.5

injectionrate = 1000
decayrate = 0.00 # 1/day

resolution = 1 #m^2
iterations = 200 

fig, (ax, ax2) = plt.subplots(2, 1, sharex= True, gridspec_kw={'height_ratios' : [2,1]})

total = injectionrate * iterations
size = np.array((300,700)) #m


mat = np.zeros(size//resolution)
walkers = np.zeros((2,total))
walkers[0,:] = int(size[0] // 2)
walkers[1,:] = int(size[1] // 10)

alive = np.ones(total, dtype = bool)


#initial_image = ax.matshow(mat ,  interpolation='nearest', norm = LogNorm(vmin=1, vmax = 50), extent = [0, size[1], size [0], 0])
initial_image = ax.matshow(mat ,  interpolation='nearest', vmin=1, vmax = 25 , extent = [0, size[1], size [0], 0], )
x_axis_plot = np.arange(0, len(mat[1]))*resolution
ax2.set_ylim(0, 500)
line = ax2.plot(x_axis_plot, np.zeros(len(mat[0])))[0]
days = ax.text(0.02, 0.92, "", transform = ax.transAxes, color = 'w', fontsize = 8)

def render_frame(frame_index):
    mat[:] = 0

    active = injectionrate * (frame_index + 1)

    XiL = np.random.normal(0, sigmaL, active)       
    XiT = np.random.normal(0, sigmaT, active)
    moveX = XiL + velocity * dt 
    moveY = XiT 
    walkers[0,:active] += moveY
    walkers[1,:active] += moveX
    inside =((0 <=walkers[0]) & (walkers[0] < size[0])) & ((0<= walkers[1]) & (walkers[1]< size[1]))
    alive[:] &= inside
    alive[:active] &= (np.random.random(active) > (decayrate * dt))

    coordinates = ((walkers[0,:active][alive[:active]]//resolution).astype(int), (walkers[1,:active][alive[:active]]//resolution).astype(int))

    np.add.at(mat, coordinates, 1)
    initial_image.set_data(mat)

    line.set_ydata(np.sum(mat, 0))

    days.set_text(f'Days: {(frame_index +  1) * dt}')
    return(initial_image, line, days)

ax.set_ylabel('Elevation through soil (m)')
ax.xaxis.set_ticks_position('bottom')

# cbar = fig.colorbar(initial_image, ax=ax)
# cbar.set_label(f'Contaminant particles per {resolution*resolution} m²')

ax2.set_xlabel('Distance through soil (m)')
ax2.xaxis.set_ticks_position('bottom')
ax2.set_ylabel(f'Contaminant particles \n per {resolution} m column')


anim = animation.FuncAnimation(
    fig = fig,
    func = render_frame,    
    frames = iterations,
    interval = 20,
    blit = True,
    repeat = False, 
    cache_frame_data= False, 
)
anim.save("spill-continuous.mp4", writer="ffmpeg", fps=30, dpi=150,
          extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"])