! filename: mytypes.f90
module mytypes

    type myarrays
        integer :: rank
        integer,allocatable :: iarr1d(:)
        real(4),allocatable :: rarr2d(:,:)
    end type

    contains

    subroutine new_my_array(new, rank)
        type (myarrays), intent(inout) :: new
        integer,intent(in) :: rank

        new%rank = rank
        if (.not.allocated(new%iarr1d)) then
            allocate(new%iarr1d(rank))
        endif
        if (.not.allocated(new%rarr2d)) then
            allocate(new%rarr2d(rank,rank))
        endif
    end subroutine new_my_array

    subroutine destroy_my_array(old)
        type (myarrays), intent(inout) :: old

        if (allocated(old%iarr1d)) then
            deallocate(old%iarr1d)
        endif
        if (allocated(old%rarr2d)) then
            deallocate(old%rarr2d)
        endif
    end subroutine destroy_my_array

end module
