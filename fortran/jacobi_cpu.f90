! Simple 2D Jacobi (5-point) with OpenMP
! Usage:
!   ./jacobi_cpu N M ITERS PREC
! where:
!   N,M   : grid size (integers, e.g., 1024 1024)
!   ITERS : number of iterations (e.g., 500)
!   PREC  : f64 or f32
!
! Output (single CSV line to stdout):
!   backend,precision,N,M,iters,runtime_ms,MLUPS,rel_error
! For rel_error, this CPU code prints 0.0 (treat as reference).

program jacobi_cpu
  use iso_fortran_env, only: wp64 => real64, wp32 => real32
  implicit none

  integer            :: N, M, iters, i, j, t
  character(len=8)   :: prec
  real(real64)       :: t0, t1, dt_ms, mlups
  logical            :: is64

  ! Pointers to allow one code path compiled once
  real(wp64), allocatable, target :: a64(:,:), b64(:,:)
  real(wp32), allocatable, target :: a32(:,:), b32(:,:)

  call parse_args(N, M, iters, prec)
  is64 = (trim(adjustl(prec)) == 'f64')

  if (is64) then
    allocate(a64(N,M), b64(N,M))
    call init64(a64, N, M)
    call cpu_time(t0)
    call jacobi64(a64, b64, N, M, iters)
    call cpu_time(t1)
    dt_ms = (t1 - t0) * 1000.0_wp64
    mlups = real((N-2)*(M-2), wp64) / (dt_ms * 1.0e3_wp64) ! MLUPS = cells / (ms*1e3)
    write(*,'(A)') csv_line('cpu','f64',N,M,iters,dt_ms,mlups,0.0_wp64)
  else
    allocate(a32(N,M), b32(N,M))
    call init32(a32, N, M)
    call cpu_time(t0)
    call jacobi32(a32, b32, N, M, iters)
    call cpu_time(t1)
    dt_ms = (t1 - t0) * 1000.0_wp64
    mlups = real((N-2)*(M-2), wp64) / (dt_ms * 1.0e3_wp64)
    write(*,'(A)') csv_line('cpu','f32',N,M,iters,dt_ms,mlups,0.0_wp64)
  end if

contains

  subroutine parse_args(N, M, iters, prec)
    integer, intent(out) :: N, M, iters
    character(len=*), intent(out) :: prec
    integer :: narg
    character(len=32) :: sN, sM, sI, sP
    narg = command_argument_count()
    if (narg < 4) then
       write(*,*) 'Usage: jacobi_cpu N M ITERS PREC   (PREC=f64|f32)'
       stop 1
    end if
    call get_command_argument(1, sN); read(sN,*) N
    call get_command_argument(2, sM); read(sM,*) M
    call get_command_argument(3, sI); read(sI,*) iters
    call get_command_argument(4, sP); prec = trim(adjustl(sP))
  end subroutine parse_args

  pure function csv_line(backend, precision, N, M, iters, ms, mlups, relerr) result(line)
    character(len=*), intent(in) :: backend, precision
    integer, intent(in)          :: N, M, iters
    real(wp64), intent(in)       :: ms, mlups, relerr
    character(len=256)           :: line
    write(line,'(A,",",A,",",I0,",",I0,",",I0,",",F0.3,",",F0.3,",",ES12.4)') &
         backend, precision, N, M, iters, ms, mlups, relerr
  end function csv_line

  subroutine init64(a, N, M)
    real(wp64), intent(inout) :: a(N,M)
    integer, intent(in) :: N, M
    integer :: i, j
    a = 0.0_wp64
    ! Dirichlet boundaries: a hot top edge as an example
    do j = 1, M
      a(1,j) = 1.0_wp64
    end do
  end subroutine init64

  subroutine init32(a, N, M)
    real(wp32), intent(inout) :: a(N,M)
    integer, intent(in) :: N, M
    integer :: i, j
    a = 0.0_wp32
    do j = 1, M
      a(1,j) = 1.0_wp32
    end do
  end subroutine init32

  subroutine jacobi64(a, b, N, M, iters)
    real(wp64), intent(inout), target :: a(N,M), b(N,M)
    integer, intent(in) :: N, M, iters
    integer :: t, i, j
    do t = 1, iters
!$omp parallel do private(j) schedule(static)
      do i = 2, N-1
        do j = 2, M-1
          b(i,j) = 0.25_wp64 * ( a(i-1,j) + a(i+1,j) + a(i,j-1) + a(i,j+1) )
        end do
      end do
!$omp end parallel do
      ! keep boundaries and swap
!$omp parallel do private(j) schedule(static)
      do i = 2, N-1
        do j = 2, M-1
          a(i,j) = b(i,j)
        end do
      end do
!$omp end parallel do
    end do
  end subroutine jacobi64

  subroutine jacobi32(a, b, N, M, iters)
    real(wp32), intent(inout), target :: a(N,M), b(N,M)
    integer, intent(in) :: N, M, iters
    integer :: t, i, j
    do t = 1, iters
!$omp parallel do private(j) schedule(static)
      do i = 2, N-1
        do j = 2, M-1
          b(i,j) = 0.25_wp32 * ( a(i-1,j) + a(i+1,j) + a(i,j-1) + a(i,j+1) )
        end do
      end do
!$omp end parallel do
!$omp parallel do private(j) schedule(static)
      do i = 2, N-1
        do j = 2, M-1
          a(i,j) = b(i,j)
        end do
      end do
!$omp end parallel do
    end do
  end subroutine jacobi32

end program jacobi_cpu
