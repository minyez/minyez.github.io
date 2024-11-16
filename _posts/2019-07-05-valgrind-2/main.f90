! filename: main.f90
program main

    use mytypes
    implicit none

    type(myarrays) :: ma

    call new_my_array(ma, 2)
    call destroy_my_array(ma)
    stop

end program
